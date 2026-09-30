# [?] metrics: fix panic for cocurrently accessing label (#3007)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2025-04-10
Source: https://github.com/bnb-chain/bsc/commit/d0d8b0f1a99f8185473c9170cec3182f12f3fd21
Type: security-commit

## Details
metrics: fix panic for cocurrently accessing label (#3007)

## Patch
### metrics/exp/exp.go
```diff
@@ -201,7 +201,7 @@ func (exp *exp) publishResettingTimer(name string, metric *metrics.ResettingTime
 }
 
 func (exp *exp) publishLabel(name string, metric *metrics.Label) {
-	labels := metric.Value()
+	labels := metric.Snapshot().Value()
 	for k, v := range labels {
 		exp.getMap(name).Set(k, exp.interfaceToExpVal(v))
 	}
```

### metrics/label.go
```diff
@@ -1,8 +1,24 @@
 package metrics
 
+import (
+	"maps"
+	"sync"
+)
+
+// LabelValue is a mapping of keys to values
+type LabelValue map[string]any
+
+// LabelSnapshot is a read-only copy of a Label.
+type LabelSnapshot LabelValue
+
+// Value returns the value at the time the snapshot was taken.
+func (l LabelSnapshot) Value() LabelValue { return LabelValue(l) }
+
 // Label is the standard implementation of a Label.
 type Label struct {
-	value map[string]interface{}
+	value LabelValue
+
+	mutex sync.Mutex
 }
 
 // GetOrRegisterLabel returns an existing Label or constructs and registers a
@@ -16,16 +32,21 @@ func GetOrRegisterLabel(name string, r Registry) *Label {
 
 // NewLabel constructs a new Label.
 func NewLabel() *Label {
-	return &Label{value: make(map[string]interface{})}
+	return &Label{value: make(map[string]any)}
 }
 
 // Value returns label values.
-func (l *Label) Value() map[string]interface{} {
-	return l.value
+func (l *Label) Snapshot() *LabelSnapshot {
+	l.mutex.Lock()
+	defer l.mutex.Unlock()
+	snapshot := LabelSnapshot(maps.Clone(l.value))
+	return &snapshot
 }
 
 // Mark records the label.
 func (l *Label) Mark(value map[string]interface{}) {
+	l.mutex.Lock()
+	defer l.mutex.Unlock()
 	for k, v := range value {
 		l.value[k] = v
 	}
```

### metrics/prometheus/collector.go
```diff
@@ -71,7 +71,7 @@ func (c *collector) Add(name string, i any) error {
 	case *metrics.ResettingTimer:
 		c.addResettingTimer(name, m.Snapshot())
 	case *metrics.Label:
-		c.addLabel(name, m)
+		c.addLabel(name, m.Snapshot())
 	default:
 		return fmt.Errorf("unknown prometheus metric type %T", i)
 	}
@@ -138,9 +138,10 @@ func (c *collector) addResettingTimer(name string, m *metrics.ResettingTimerSnap
 	c.buff.WriteRune('\n')
 }
 
-func (c *collector) addLabel(name string, m *metrics.Label) {
-	labels := make([]string, 0, len(m.Value()))
-	for k, v := range m.Value() {
+func (c *collector) addLabel(name string, m *metrics.LabelSnapshot) {
+	labelValue := m.Value()
+	labels := make([]string, 0, len(labelValue))
+	for k, v := range labelValue {
 		labels = append(labels, fmt.Sprintf(`%s="%s"`, mutateKey(k), fmt.Sprint(v)))
 	}
 	c.writeLabel(mutateKey(name), "{"+strings.Join(labels, ", ")+"}")
```
