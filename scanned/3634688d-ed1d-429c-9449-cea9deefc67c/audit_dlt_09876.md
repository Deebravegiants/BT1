# [?] fix(apps-ui-kit): text overflowing tooltip (#2737)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-09-23
Source: https://github.com/iotaledger/iota/commit/cf175de3cfd99bef341ae84bbdb648aa01193936
Type: security-commit

## Details
fix(apps-ui-kit): text overflowing tooltip (#2737)

* fix: tooltip overflowing text

* fix: words overflow in DisplayStats

* fix: make tooltip take the max width if possible

## Patch
### apps/ui-kit/src/lib/components/atoms/tooltip/Tooltip.tsx
```diff
@@ -22,12 +22,12 @@ export function Tooltip({
             {children}
             <div
                 className={cx(
-                    'absolute z-[999] hidden w-max max-w-[200px] rounded bg-neutral-80 p-xs text-neutral-10 opacity-0 transition-opacity duration-300 group-hover:flex group-hover:opacity-100 group-focus:opacity-100 dark:bg-neutral-30 dark:text-neutral-92',
+                    'absolute z-[999] hidden w-max max-w-[200px] rounded bg-neutral-80 p-xs text-neutral-10 opacity-0 transition-opacity duration-300 group-hover:block group-hover:opacity-100 group-focus:opacity-100 dark:bg-neutral-30 dark:text-neutral-92',
                     tooltipPositionClass,
                 )}
                 role="tooltip"
             >
-                {text}
+                <p className="w-full break-words">{text}</p>
             </div>
         </div>
     );
```
