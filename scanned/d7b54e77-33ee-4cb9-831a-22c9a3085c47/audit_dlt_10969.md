# [?] fix: err instead of panic when recursively solving hints

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2022-03-28
Source: https://github.com/Consensys-Incorporated/gnark/commit/1dd705963d032943cd41eac17540a4be304e7c04
Type: security-commit

## Details
fix: err instead of panic when recursively solving hints

## Patch
### internal/backend/bls12-377/cs/solution.go
```diff
@@ -159,18 +159,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint.
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -184,12 +181,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```

### internal/backend/bls12-381/cs/solution.go
```diff
@@ -159,18 +159,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint.
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -184,12 +181,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```

### internal/backend/bls24-315/cs/solution.go
```diff
@@ -159,18 +159,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint.
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -184,12 +181,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```

### internal/backend/bn254/cs/solution.go
```diff
@@ -159,18 +159,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint.
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -184,12 +181,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```

### internal/backend/bw6-633/cs/solution.go
```diff
@@ -159,18 +159,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint.
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -184,12 +181,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```

### internal/backend/bw6-761/cs/solution.go
```diff
@@ -159,18 +159,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint.
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -184,12 +181,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```

### internal/generator/backend/template/representations/solution.go.tmpl
```diff
@@ -139,18 +139,15 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 	// is the output of another hint. 
 	// it is safe to recursively solve this with the parallel solver, since all hints-output wires 
 	// that we can solve this way are marked to be solved with the current constraint we are processing.
-	solveOrPanic := func(t compiled.Term) {
+	recursiveSolve := func(t compiled.Term) error {
 		wID := t.WireID()
 		if s.solved[wID] {
-			return
+			return nil
 		}
 		// unsolved dependency
 		if h, ok := s.mHints[wID]; ok {
 			// solve recursively.
-			if err := s.solveWithHint(wID, h); err != nil {
-				panic(err)
-			}
-			return 
+			return s.solveWithHint(wID, h)
 		}
 
 		// it's not a hint, we panic.
@@ -164,12 +161,16 @@ func (s *solution) solveWithHint(vID int, h *compiled.Hint) error {
 		case compiled.LinearExpression:
 			var v fr.Element
 			for _, term := range t {
-				solveOrPanic(term)
+				if err := recursiveSolve(term); err != nil {
+					return err
+				}
 				s.accumulateInto(term, &v)
 			}
 			v.ToBigIntRegular(inputs[i])
 		case compiled.Term:
-			solveOrPanic(t)
+			if err := recursiveSolve(t); err != nil {
+				return err
+			}
 			v := s.computeTerm(t)
 			v.ToBigIntRegular(inputs[i])
 		default:
```
