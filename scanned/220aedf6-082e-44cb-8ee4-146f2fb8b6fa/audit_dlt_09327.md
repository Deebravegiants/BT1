# [?] fix: overflow of memory offset or size in debugger (#6474)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2023-11-30
Source: https://github.com/foundry-rs/foundry/commit/f5c91995f80b5bf3b4c29c934d414cc198c9e7a8
Type: security-commit

## Details
fix: overflow of memory offset or size in debugger (#6474)

* fix overflow of memory offset or size in debugger

* fix fmt

## Patch
### crates/debugger/src/lib.rs
```diff
@@ -894,7 +894,7 @@ Line::from(Span::styled("[t]: stack labels | [m]: memory decoding | [shift + j/k
             -2 => Some(1),
             -1 => Some(32),
             0 => None,
-            1.. => Some(stack[stack_len - stack_index as usize].to()),
+            1.. => Some(stack[stack_len - stack_index as usize].saturating_to()),
             _ => panic!("invalid stack index"),
         };
 
@@ -917,7 +917,7 @@ Line::from(Span::styled("[t]: stack labels | [m]: memory decoding | [shift + j/k
         draw_mem: &DrawMemory,
     ) {
         let memory = &debug_steps[current_step].memory;
-        let stack_space = Block::default()
+        let memory_space = Block::default()
             .title(format!("Memory (max expansion: {} bytes)", memory.len()))
             .borders(Borders::ALL);
         let max_i = memory.len() / 32;
@@ -1023,7 +1023,7 @@ Line::from(Span::styled("[t]: stack labels | [m]: memory decoding | [shift + j/k
                 Line::from(spans)
             })
             .collect();
-        let paragraph = Paragraph::new(text).block(stack_space).wrap(Wrap { trim: true });
+        let paragraph = Paragraph::new(text).block(memory_space).wrap(Wrap { trim: true });
         f.render_widget(paragraph, area);
     }
 }
```
