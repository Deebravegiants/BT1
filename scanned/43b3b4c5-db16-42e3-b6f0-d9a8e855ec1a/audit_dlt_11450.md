# [?] [fix] Handle panics correctly in the flakey test runner (#10734)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-09-21
Source: https://github.com/smartcontractkit/ccip/commit/7ca79f56eb4be56306b1f1def76fa382143337c8
Type: security-commit

## Details
[fix] Handle panics correctly in the flakey test runner (#10734)

- Previously we would run tests multiple times via the -count=N flag on
  the `go test` command. This worked well, except it didn't handle tests
  that panic'd correctly. In that case, the test would only get run once.
  To handle this correctly we instead run each test command multiple
  times, and tally failures across the multiple runs.

## Patch
### tools/flakeytests/reporter.go
```diff
@@ -45,12 +45,12 @@ type LokiReporter struct {
 	ctx     Context
 }
 
-func (l *LokiReporter) createRequest(flakeyTests map[string][]string) (pushRequest, error) {
+func (l *LokiReporter) createRequest(flakeyTests map[string]map[string]struct{}) (pushRequest, error) {
 	vs := [][]string{}
 	now := l.now()
 	nows := fmt.Sprintf("%d", now.UnixNano())
 	for pkg, tests := range flakeyTests {
-		for _, t := range tests {
+		for t := range tests {
 			d, err := json.Marshal(flakeyTest{
 				Package:    pkg,
 				TestName:   t,
@@ -117,7 +117,7 @@ func (l *LokiReporter) makeRequest(pushReq pushRequest) error {
 	return err
 }
 
-func (l *LokiReporter) Report(flakeyTests map[string][]string) error {
+func (l *LokiReporter) Report(flakeyTests map[string]map[string]struct{}) error {
 	pushReq, err := l.createRequest(flakeyTests)
 	if err != nil {
 		return err
```

### tools/flakeytests/reporter_test.go
```diff
@@ -12,15 +12,17 @@ import (
 func TestMakeRequest_SingleTest(t *testing.T) {
 	now := time.Now()
 	ts := fmt.Sprintf("%d", now.UnixNano())
-	ft := map[string][]string{
-		"core/assets": {"TestLink"},
+	ft := map[string]map[string]struct{}{
+		"core/assets": map[string]struct{}{
+			"TestLink": struct{}{},
+		},
 	}
 	lr := &LokiReporter{auth: "bla", host: "bla", command: "go_core_tests", now: func() time.Time { return now }}
 	pr, err := lr.createRequest(ft)
 	require.NoError(t, err)
 	assert.Len(t, pr.Streams, 1)
 	assert.Equal(t, pr.Streams[0].Stream, map[string]string{"command": "go_core_tests", "app": "flakey-test-reporter"})
-	assert.Equal(t, pr.Streams[0].Values, [][]string{
+	assert.ElementsMatch(t, pr.Streams[0].Values, [][]string{
 		{ts, "{\"package\":\"core/assets\",\"test_name\":\"TestLink\",\"fq_test_name\":\"core/assets:TestLink\"}"},
 		{ts, "{\"num_flakes\":1}"},
 	})
@@ -29,16 +31,19 @@ func TestMakeRequest_SingleTest(t *testing.T) {
 func TestMakeRequest_MultipleTests(t *testing.T) {
 	now := time.Now()
 	ts := fmt.Sprintf("%d", now.UnixNano())
-	ft := map[string][]string{
-		"core/assets": {"TestLink", "TestCore"},
+	ft := map[string]map[string]struct{}{
+		"core/assets": map[string]struct{}{
+			"TestLink": struct{}{},
+			"TestCore": struct{}{},
+		},
 	}
 	lr := &LokiReporter{auth: "bla", host: "bla", command: "go_core_tests", now: func() time.Time { return now }}
 	pr, err := lr.createRequest(ft)
 	require.NoError(t, err)
 	assert.Len(t, pr.Streams, 1)
 	assert.Equal(t, pr.Streams[0].Stream, map[string]string{"command": "go_core_tests", "app": "flakey-test-reporter"})
 
-	assert.Equal(t, pr.Streams[0].Values, [][]string{
+	assert.ElementsMatch(t, pr.Streams[0].Values, [][]string{
 		{ts, "{\"package\":\"core/assets\",\"test_name\":\"TestLink\",\"fq_test_name\":\"core/assets:TestLink\"}"},
 		{ts, "{\"package\":\"core/assets\",\"test_name\":\"TestCore\",\"fq_test_name\":\"core/assets:TestCore\"}"},
 		{ts, "{\"num_flakes\":2}"},
@@ -48,27 +53,27 @@ func TestMakeRequest_MultipleTests(t *testing.T) {
 func TestMakeRequest_NoTests(t *testing.T) {
 	now := time.Now()
 	ts := fmt.Sprintf("%d", now.UnixNano())
-	ft := map[string][]string{}
+	ft := map[string]map[string]struct{}{}
 	lr := &LokiReporter{auth: "bla", host: "bla", command: "go_core_tests", now: func() time.Time { return now }}
 	pr, err := lr.createRequest(ft)
 	require.NoError(t, err)
 	assert.Len(t, pr.Streams, 1)
 	assert.Equal(t, pr.Streams[0].Stream, map[string]string{"command": "go_core_tests", "app": "flakey-test-reporter"})
-	assert.Equal(t, pr.Streams[0].Values, [][]string{
+	assert.ElementsMatch(t, pr.Streams[0].Values, [][]string{
 		{ts, "{\"num_flakes\":0}"},
 	})
 }
 
 func TestMakeRequest_WithContext(t *testing.T) {
 	now := time.Now()
 	ts := fmt.Sprintf("%d", now.UnixNano())
-	ft := map[string][]string{}
+	ft := map[string]map[string]struct{}{}
 	lr := &LokiReporter{auth: "bla", host: "bla", command: "go_core_tests", now: func() time.Time { return now }, ctx: Context{CommitSHA: "42"}}
 	pr, err := lr.createRequest(ft)
 	require.NoError(t, err)
 	assert.Len(t, pr.Streams, 1)
 	assert.Equal(t, pr.Streams[0].Stream, map[string]string{"command": "go_core_tests", "app": "flakey-test-reporter"})
-	assert.Equal(t, pr.Streams[0].Values, [][]string{
+	assert.ElementsMatch(t, pr.Streams[0].Values, [][]string{
 		{ts, "{\"num_flakes\":0,\"commit_sha\":\"42\"}"},
 	})
 }
```

### tools/flakeytests/runner.go
```diff
@@ -20,37 +20,53 @@ var (
 )
 
 type Runner struct {
-	readers   []io.Reader
-	numReruns int
-	runTestFn runTestCmd
-	parse     parseFn
-	reporter  reporter
+	readers     []io.Reader
+	testCommand tester
+	numReruns   int
+	parse       parseFn
+	reporter    reporter
+}
+
+type tester interface {
+	test(pkg string, tests []string, w io.Writer) error
 }
 
 type reporter interface {
-	Report(map[string][]string) error
+	Report(map[string]map[string]struct{}) error
 }
 
-type runTestCmd func(pkg string, testNames []string, numReruns int, w io.Writer) error
 type parseFn func(readers ...io.Reader) (map[string]map[string]int, error)
 
 func NewRunner(readers []io.Reader, reporter reporter, numReruns int) *Runner {
-	return &Runner{
-		readers:   readers,
+	tc := &testCommand{
+		repo:      "github.com/smartcontractkit/chainlink/v2",
+		command:   "./tools/bin/go_core_tests",
 		numReruns: numReruns,
-		runTestFn: runGoTest,
-		parse:     parseOutput,
-		reporter:  reporter,
+	}
+	return &Runner{
+		readers:     readers,
+		numReruns:   numReruns,
+		testCommand: tc,
+		parse:       parseOutput,
+		reporter:    reporter,
 	}
 }
 
-func runGoTest(pkg string, tests []string, numReruns int, w io.Writer) error {
-	pkg = strings.Replace(pkg, "github.com/smartcontractkit/chainlink/v2", "", -1)
+type testCommand struct {
+	command   string
+	repo      string
+	numReruns int
+	overrides func(*exec.Cmd)
+}
+
+func (t *testCommand) test(pkg string, tests []string, w io.Writer) error {
+	replacedPkg := strings.Replace(pkg, t.repo, "", -1)
 	testFilter := strings.Join(tests, "|")
-	cmd := exec.Command("./tools/bin/go_core_tests", fmt.Sprintf(".%s", pkg)) //#nosec
-	cmd.Env = append(os.Environ(), fmt.Sprintf("TEST_FLAGS=-count %d -run %s", numReruns, testFilter))
+	cmd := exec.Command(t.command, fmt.Sprintf(".%s", replacedPkg)) //#nosec
+	cmd.Env = append(os.Environ(), fmt.Sprintf("TEST_FLAGS=-count=%d -run %s", t.numReruns, testFilter))
 	cmd.Stdout = io.MultiWriter(os.Stdout, w)
 	cmd.Stderr = io.MultiWriter(os.Stderr, w)
+	t.overrides(cmd)
 	return cmd.Run()
 }
 
@@ -123,30 +139,50 @@ type exitCoder interface {
 	ExitCode() int
 }
 
-func (r *Runner) runTests(failedTests map[string]map[string]int) (io.Reader, error) {
-	var out bytes.Buffer
+func (r *Runner) runTests(failedTests map[string]map[string]int) (map[string]map[string]struct{}, error) {
+	suspectedFlakes := map[string]map[string]struct{}{}
+
 	for pkg, tests := range failedTests {
 		ts := []string{}
 		for test := range tests {
 			ts = append(ts, test)
 		}
 
 		log.Printf("Executing test command with parameters: pkg=%s, tests=%+v, numReruns=%d\n", pkg, ts, r.numReruns)
-		err := r.runTestFn(pkg, ts, r.numReruns, &out)
-		if err != nil {
-			log.Printf("Test command errored: %s\n", err)
-			// There was an error because the command failed with a non-zero
-			// exit code. This could just mean that the test failed again, so let's
-			// keep going.
-			var exErr exitCoder
-			if errors.As(err, &exErr) && exErr.ExitCode() > 0 {
-				continue
+		for i := 0; i < r.numReruns; i++ {
+			var out bytes.Buffer
+
+			err := r.testCommand.test(pkg, ts, &out)
+			if err != nil {
+				log.Printf("Test command errored: %s\n", err)
+				// There was an error because the command failed with a non-zero
+				// exit code. This could just mean that the test failed again, so let's
+				// keep going.
+				var exErr exitCoder
+				if errors.As(err, &exErr) && exErr.ExitCode() > 0 {
+					continue
+				}
+				return suspectedFlakes, err
+			}
+
+			fr, err := r.parse(&out)
+			if err != nil {
+				return nil, err
+			}
+
+			for t := range tests {
+				failures := fr[pkg][t]
+				if failures == 0 {
+					if suspectedFlakes[pkg] == nil {
+						suspectedFlakes[pkg] = map[string]struct{}{}
+					}
+					suspectedFlakes[pkg][t] = struct{}{}
+				}
 			}
-			return &out, err
 		}
 	}
 
-	return &out, nil
+	return suspectedFlakes, nil
 }
 
 func (r *Runner) Run() error {
@@ -155,28 +191,11 @@ func (r *Runner) Run() error {
 		return err
 	}
 
-	output, err := r.runTests(failedTests)
+	suspectedFlakes, err := r.runTests(failedTests)
 	if err != nil {
 		return err
 	}
 
-	failedReruns, err := r.parse(output)
-	if err != nil {
-		return err
-	}
-
-	suspectedFlakes := map[string][]string{}
-	// A test is flakey if it appeared in the list of original flakey tests
-	// and doesn't appear in the reruns, or if it hasn't failed each additional
-	// run, i.e. if it hasn't twice after being re-run.
-	for pkg, t := range failedTests {
-		for test := range t {
-			if failedReruns[pkg][test] != r.numReruns {
-				suspectedFlakes[pkg] = append(suspectedFlakes[pkg], test)
-			}
-		}
-	}
-
 	if len(suspectedFlakes) > 0 {
 		log.Printf("ERROR: Suspected flakes found: %+v\n", suspectedFlakes)
 	} else {
```

### tools/flakeytests/runner_test.go
```diff
@@ -1,7 +1,10 @@
 package flakeytests
 
 import (
+	"fmt"
 	"io"
+	"os"
+	"os/exec"
 	"strings"
 	"testing"
 
@@ -10,16 +13,16 @@ import (
 )
 
 type mockReporter struct {
-	entries map[string][]string
+	entries map[string]map[string]struct{}
 }
 
-func (m *mockReporter) Report(entries map[string][]string) error {
+func (m *mockReporter) Report(entries map[string]map[string]struct{}) error {
 	m.entries = entries
 	return nil
 }
 
 func newMockReporter() *mockReporter {
-	return &mockReporter{entries: map[string][]string{}}
+	return &mockReporter{entries: map[string]map[string]struct{}{}}
 }
 
 func TestParser(t *testing.T) {
@@ -86,16 +89,29 @@ func TestParser_SuccessfulOutput(t *testing.T) {
 	assert.Len(t, ts, 0)
 }
 
+type testAdapter func(string, []string, io.Writer) error
+
+func (t testAdapter) test(pkg string, tests []string, out io.Writer) error {
+	return t(pkg, tests, out)
+}
+
 func TestRunner_WithFlake(t *testing.T) {
-	output := `{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`
+	initialOutput := `{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`
+	outputs := []string{
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+		``,
+	}
 	m := newMockReporter()
+	i := 0
 	r := &Runner{
 		numReruns: 2,
-		readers:   []io.Reader{strings.NewReader(output)},
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
-			_, err := w.Write([]byte(output))
+		readers:   []io.Reader{strings.NewReader(initialOutput)},
+
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
+			_, err := w.Write([]byte(outputs[i]))
+			i++
 			return err
-		},
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
@@ -105,22 +121,32 @@ func TestRunner_WithFlake(t *testing.T) {
 	err := r.Run()
 	require.NoError(t, err)
 	assert.Len(t, m.entries, 1)
-	assert.Equal(t, m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"], []string{"TestLink"})
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"]["TestLink"]
+	assert.True(t, ok)
 }
 
 func TestRunner_WithFailedPackage(t *testing.T) {
-	output := `
+	initialOutput := `
 {"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
 {"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Elapsed":0}
 `
+	outputs := []string{`
+{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
+{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Elapsed":0}
+`,
+		``,
+	}
+
 	m := newMockReporter()
+	i := 0
 	r := &Runner{
 		numReruns: 2,
-		readers:   []io.Reader{strings.NewReader(output)},
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
-			_, err := w.Write([]byte(output))
+		readers:   []io.Reader{strings.NewReader(initialOutput)},
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
+			_, err := w.Write([]byte(outputs[i]))
+			i++
 			return err
-		},
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
@@ -130,7 +156,8 @@ func TestRunner_WithFailedPackage(t *testing.T) {
 	err := r.Run()
 	require.NoError(t, err)
 	assert.Len(t, m.entries, 1)
-	assert.Equal(t, m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"], []string{"TestLink"})
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"]["TestLink"]
+	assert.True(t, ok)
 }
 
 func TestRunner_AllFailures(t *testing.T) {
@@ -144,10 +171,10 @@ func TestRunner_AllFailures(t *testing.T) {
 	r := &Runner{
 		numReruns: 2,
 		readers:   []io.Reader{strings.NewReader(output)},
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
 			_, err := w.Write([]byte(rerunOutput))
 			return err
-		},
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
@@ -160,25 +187,28 @@ func TestRunner_AllFailures(t *testing.T) {
 func TestRunner_RerunSuccessful(t *testing.T) {
 	output := `{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`
 
-	rerunOutput := `
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"pass","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
-`
+	rerunOutputs := []string{
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"pass","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+	}
 	m := newMockReporter()
+	i := 0
 	r := &Runner{
 		numReruns: 2,
 		readers:   []io.Reader{strings.NewReader(output)},
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
-			_, err := w.Write([]byte(rerunOutput))
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
+			_, err := w.Write([]byte(rerunOutputs[i]))
+			i++
 			return err
-		},
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
 
 	err := r.Run()
 	require.NoError(t, err)
-	assert.Equal(t, m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"], []string{"TestLink"})
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"]["TestLink"]
+	assert.True(t, ok)
 }
 
 func TestRunner_RootLevelTest(t *testing.T) {
@@ -189,17 +219,18 @@ func TestRunner_RootLevelTest(t *testing.T) {
 	r := &Runner{
 		numReruns: 2,
 		readers:   []io.Reader{strings.NewReader(output)},
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
 			_, err := w.Write([]byte(rerunOutput))
 			return err
-		},
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
 
 	err := r.Run()
 	require.NoError(t, err)
-	assert.Equal(t, m.entries["github.com/smartcontractkit/chainlink/v2/"], []string{"TestConfigDocs"})
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/"]["TestConfigDocs"]
+	assert.True(t, ok)
 }
 
 type exitError struct{}
@@ -211,25 +242,28 @@ func (e *exitError) Error() string { return "exit code: 1" }
 func TestRunner_RerunFailsWithNonzeroExitCode(t *testing.T) {
 	output := `{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`
 
-	rerunOutput := `
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"pass","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
-`
+	rerunOutputs := []string{
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"pass","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+	}
 	m := newMockReporter()
+	i := 0
 	r := &Runner{
 		numReruns: 2,
 		readers:   []io.Reader{strings.NewReader(output)},
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
-			_, _ = w.Write([]byte(rerunOutput))
-			return &exitError{}
-		},
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
+			_, err := w.Write([]byte(rerunOutputs[i]))
+			i++
+			return err
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
 
 	err := r.Run()
 	require.NoError(t, err)
-	assert.Equal(t, m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"], []string{"TestLink"})
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"]["TestLink"]
+	assert.True(t, ok)
 }
 
 func TestRunner_RerunWithNonZeroExitCodeDoesntStopCommand(t *testing.T) {
@@ -243,34 +277,66 @@ func TestRunner_RerunWithNonZeroExitCodeDoesntStopCommand(t *testing.T) {
 	}
 
 	rerunOutputs := []string{
-		`
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"pass","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}
-`,
-		`
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/services/vrf/v2","Test":"TestMaybeReservedLinkV2","Elapsed":0}
-{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/services/vrf/v2","Test":"TestMaybeReservedLinkV2","Elapsed":0}
-`,
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"pass","Package":"github.com/smartcontractkit/chainlink/v2/core/assets","Test":"TestLink","Elapsed":0}`,
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/services/vrf/v2","Test":"TestMaybeReservedLinkV2","Elapsed":0}`,
+		`{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/core/services/vrf/v2","Test":"TestMaybeReservedLinkV2","Elapsed":0}`,
 	}
 
 	index := 0
 	m := newMockReporter()
 	r := &Runner{
 		numReruns: 2,
 		readers:   outputs,
-		runTestFn: func(pkg string, testNames []string, numReruns int, w io.Writer) error {
-
-			_, _ = w.Write([]byte(rerunOutputs[index]))
+		testCommand: testAdapter(func(pkg string, testNames []string, w io.Writer) error {
+			_, err := w.Write([]byte(rerunOutputs[index]))
 			index++
-			return &exitError{}
-		},
+			return err
+		}),
 		parse:    parseOutput,
 		reporter: m,
 	}
 
 	err := r.Run()
 	require.NoError(t, err)
 	calls := index
-	assert.Equal(t, 2, calls)
-	assert.Equal(t, m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"], []string{"TestLink"})
+	assert.Equal(t, 4, calls)
+
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/core/assets"]["TestLink"]
+	assert.True(t, ok)
+}
+
+// Used for integration tests
+func TestSkippedForTests(t *testing.T) {
+	if os.Getenv("FLAKEY_TEST_RUNNER_RUN_FIXTURE_TEST") != "1" {
+		t.Skip()
+	}
+
+	go func() {
+		panic("skipped test")
+	}()
+}
+
+func TestParsesPanicCorrectly(t *testing.T) {
+	output := `{"Time":"2023-09-07T15:39:46.378315+01:00","Action":"fail","Package":"github.com/smartcontractkit/chainlink/v2/tools/flakeytests/","Test":"TestSkippedForTests","Elapsed":0}`
+
+	m := newMockReporter()
+	r := &Runner{
+		numReruns: 2,
+		readers:   []io.Reader{strings.NewReader(output)},
+		testCommand: testAdapter(func(pkg string, tests []string, w io.Writer) error {
+			pkg = strings.Replace(pkg, "github.com/smartcontractkit/chainlink/v2/tools/flakeytests", "", -1)
+			testFilter := strings.Join(tests, "|")
+			cmd := exec.Command("../bin/go_core_tests", fmt.Sprintf(".%s", pkg)) //#nosec
+			cmd.Env = append(os.Environ(), "FLAKEY_TESTRUNNER_RUN_FIXTURE_TEST=1", fmt.Sprintf("TEST_FLAGS=-run %s", testFilter))
+			return cmd.Run()
+		}),
+		parse:    parseOutput,
+		reporter: m,
+	}
+
+	err := r.Run()
+	require.NoError(t, err)
+	_, ok := m.entries["github.com/smartcontractkit/chainlink/v2/tools/flakeytests"]["TestSkippedForTests"]
+	assert.False(t, ok)
 }
```
