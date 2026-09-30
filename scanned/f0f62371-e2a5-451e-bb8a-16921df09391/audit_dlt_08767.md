# [?] cmd/disasm: fix array-out-of-bounds error (#3491)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-01-08
Source: https://github.com/scroll-tech/go-ethereum/commit/0a5450fe0453d2a443dfca50d1106b9dbdb7a8fe
Type: security-commit

## Details
cmd/disasm: fix array-out-of-bounds error (#3491)

## Patch
### cmd/disasm/main.go
```diff
@@ -42,15 +42,19 @@ func main() {
 
 	for pc := uint64(0); pc < uint64(len(code)); pc++ {
 		op := vm.OpCode(code[pc])
-		fmt.Printf("%-5d  %v", pc, op)
 
 		switch op {
 		case vm.PUSH1, vm.PUSH2, vm.PUSH3, vm.PUSH4, vm.PUSH5, vm.PUSH6, vm.PUSH7, vm.PUSH8, vm.PUSH9, vm.PUSH10, vm.PUSH11, vm.PUSH12, vm.PUSH13, vm.PUSH14, vm.PUSH15, vm.PUSH16, vm.PUSH17, vm.PUSH18, vm.PUSH19, vm.PUSH20, vm.PUSH21, vm.PUSH22, vm.PUSH23, vm.PUSH24, vm.PUSH25, vm.PUSH26, vm.PUSH27, vm.PUSH28, vm.PUSH29, vm.PUSH30, vm.PUSH31, vm.PUSH32:
 			a := uint64(op) - uint64(vm.PUSH1) + 1
-			fmt.Printf("  => %x", code[pc+1:pc+1+a])
-
+			u := pc + 1 + a
+			if uint64(len(code)) <= pc || uint64(len(code)) < u {
+				fmt.Printf("Error: incomplete push instruction at %v\n", pc)
+				return
+			}
+			fmt.Printf("%-5d  %v  => %x\n", pc, op, code[pc+1:u])
 			pc += a
+		default:
+			fmt.Printf("%-5d  %v\n", pc, op)
 		}
-		fmt.Println()
 	}
 }
```
