# TradingAgents/graph/tracing.py

import os
from typing import Dict, Any, Optional
import warnings


class PhoenixTracer:
    """Manages Phoenix (Arize) tracing setup for TradingAgents using OpenTelemetry."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Phoenix tracer with config.

        Args:
            config: Configuration dictionary containing tracing settings
        """
        self.config = config
        self.enabled = config.get("phoenix_tracing", False)
        self.is_active = False

    def setup(self) -> bool:
        """Set up Phoenix tracing with OpenTelemetry.

        Returns:
            True if setup successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.resources import Resource
            from openinference.instrumentation.langchain import LangChainInstrumentor

            # Get configuration
            endpoint = self.config.get(
                "phoenix_collector_endpoint", "http://localhost:4317"
            )
            project = self.config.get("phoenix_project", "tradingagents")

            # Create resource with project name
            resource = Resource.create({"service.name": project})

            # Set up tracer provider
            tracer_provider = TracerProvider(resource=resource)

            # Create OTLP exporter pointing to Phoenix
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)

            # Add span processor
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)

            # Set as global tracer provider
            trace.set_tracer_provider(tracer_provider)

            # Instrument LangChain
            LangChainInstrumentor().instrument()

            self.is_active = True

            print("=" * 60)
            print("✓ Phoenix Tracing Enabled")
            print("=" * 60)
            print(f"Project: {project}")
            print(f"Collector Endpoint: {endpoint}")
            print(f"View traces at: http://localhost:6006/")
            print("=" * 60 + "\n")

            return True

        except ImportError as e:
            warnings.warn(
                f"Phoenix tracing dependencies not installed: {e}\n"
                "Install with: pip install opentelemetry-api opentelemetry-sdk "
                "opentelemetry-exporter-otlp openinference-instrumentation-langchain"
            )
            return False
        except Exception as e:
            warnings.warn(f"Failed to setup Phoenix tracing: {e}")
            return False

    def cleanup(self):
        """Clean up Phoenix tracing resources."""
        if self.is_active:
            try:
                from openinference.instrumentation.langchain import (
                    LangChainInstrumentor,
                )

                LangChainInstrumentor().uninstrument()
            except Exception:
                pass
            self.is_active = False

    def add_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add tracing metadata to be included in traces.

        Args:
            metadata: Existing metadata dictionary

        Returns:
            Updated metadata dictionary
        """
        if not self.is_active:
            return metadata

        metadata["phoenix_enabled"] = True
        metadata["phoenix_project"] = self.config.get("phoenix_project")
        return metadata
