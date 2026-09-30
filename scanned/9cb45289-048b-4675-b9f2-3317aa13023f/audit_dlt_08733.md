# [?] fix(kt-devnet): data race in docker build code (#15342)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-04-10
Source: https://github.com/ethereum-optimism/optimism/commit/a523064bb3d0377a5199e3acfbc0950664dbead5
Type: security-commit

## Details
fix(kt-devnet): data race in docker build code (#15342)

## Patch
### kurtosis-devnet/pkg/build/docker.go
```diff
@@ -233,15 +233,17 @@ type templateData struct {
 // Build ensures the docker image for the given project is built, respecting concurrency limits.
 // It blocks until the specific requested build is complete. Other builds may run concurrently.
 func (b *DockerBuilder) Build(projectName, imageTag string) (string, error) {
+	b.mu.Lock()
 	state, exists := b.buildStates[projectName]
 	if !exists {
 		state = &buildState{
 			done: make(chan struct{}),
 		}
-		b.mu.Lock()
 		b.buildStates[projectName] = state
-		b.mu.Unlock()
+	}
+	b.mu.Unlock()
 
+	if !exists {
 		state.once.Do(func() {
 			err := b.executeBuild(projectName, imageTag, state)
 			if err != nil {
```
