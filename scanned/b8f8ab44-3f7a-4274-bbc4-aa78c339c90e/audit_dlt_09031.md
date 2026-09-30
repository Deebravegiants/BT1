# [?] Fix race condition in gauge update [PLEN-86] (#16009)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2023-01-09
Source: https://github.com/digital-asset/daml/commit/a7b7a9af1f598069e1eaf8366960bf7175031bc3
Type: security-commit

## Details
Fix race condition in gauge update [PLEN-86] (#16009)

## Patch
### observability/metrics/src/main/scala/com/daml/metrics/api/MetricHandle.scala
```diff
@@ -117,7 +117,7 @@ object MetricHandle {
 
     def updateValue(newValue: T): Unit
 
-    def updateValue(f: T => T): Unit = updateValue(f(getValue))
+    def updateValue(f: T => T): Unit
 
     def getValue: T
   }
```

### observability/metrics/src/main/scala/com/daml/metrics/api/dropwizard/Metrics.scala
```diff
@@ -70,6 +70,8 @@ sealed case class DropwizardCounter(name: String, metric: codahale.Counter) exte
 sealed case class DropwizardGauge[T](name: String, metric: Gauges.VarGauge[T]) extends Gauge[T] {
   def updateValue(newValue: T): Unit = metric.updateValue(newValue)
   override def getValue: T = metric.getValue
+
+  override def updateValue(f: T => T): Unit = metric.updateValue(f)
 }
 
 sealed case class DropwizardHistogram(name: String, metric: codahale.Histogram)
```

### observability/metrics/src/main/scala/com/daml/metrics/api/noop/Metrics.scala
```diff
@@ -35,6 +35,7 @@ case class NoOpGauge[T](name: String, value: T) extends Gauge[T] {
 
   override def getValue: T = value
 
+  override def updateValue(f: T => T): Unit = ()
 }
 
 case class NoOpMeter(name: String) extends Meter {
```

### observability/metrics/src/main/scala/com/daml/metrics/api/opentelemetry/OpenTelemetryFactory.scala
```diff
@@ -205,6 +205,7 @@ case class OpenTelemetryGauge[T](name: String, varGauge: VarGauge[T]) extends Ga
 
   override def getValue: T = varGauge.getValue
 
+  override def updateValue(f: T => T): Unit = varGauge.updateValue(f)
 }
 
 case class OpenTelemetryMeter(name: String, counter: LongCounter, meterContext: MetricsContext)
```

### observability/metrics/src/test/lib/scala/com/daml/metrics/api/testing/InMemoryMetricsFactory.scala
```diff
@@ -108,6 +108,8 @@ object InMemoryMetricsFactory extends InMemoryMetricsFactory {
       value.set(newValue)
 
     override def getValue: T = value.get()
+
+    override def updateValue(f: T => T): Unit = discard(value.updateAndGet((t: T) => f(t)))
   }
 
   case class InMemoryMeter(initialContext: MetricsContext) extends Meter {
```
