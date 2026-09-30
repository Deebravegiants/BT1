# [?] fix address overflow on long prefix match

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-10-04
Source: https://github.com/mempool/mempool/commit/6c7673c97ffc0ba5b7872f9d91217e0d9fcb0d28
Type: security-commit

## Details
fix address overflow on long prefix match

## Patch
### frontend/src/app/shared/components/address-text/address-text.component.html
```diff
@@ -2,9 +2,9 @@
 @if (similarity) {
   <div class="address-text">
     <a class="address" style="display: contents;" [routerLink]="['/address/' | relativeUrl, address]" title="{{ address }}">
-      <span class="prefix">{{ similarity.match.prefix }}</span>
-      <span class="infix" [ngStyle]="{'text-decoration-color': groupColors[similarity.group % (groupColors.length)]}">{{ address.slice(similarity.match.prefix.length || 0, -similarity.match.postfix.length || undefined) }}</span>
-      <span class="postfix"> {{ similarity.match.postfix }}</span>
+      <span class="prefix">{{ similarity.match.prefix.slice(0, 16) }}</span>
+      <span class="infix" [ngStyle]="{'text-decoration-color': groupColors[similarity.group % (groupColors.length)]}">{{ address.slice(min(similarity.match.prefix.length, 16) || 0, -min(similarity.match.postfix.length, 16) || undefined) }}</span>
+      <span class="postfix"> {{ similarity.match.postfix.slice(-16) }}</span>
     </a>
     <span class="poison-alert" *ngIf="similarity" i18n-ngbTooltip="address-poisoning.warning-tooltip" ngbTooltip="This address is deceptively similar to another output. It may be part of an address poisoning attack.">
       <fa-icon [icon]="['fas', 'exclamation-triangle']" [fixedWidth]="true"></fa-icon>
```

### frontend/src/app/shared/components/address-text/address-text.component.ts
```diff
@@ -11,6 +11,8 @@ export class AddressTextComponent {
   @Input() info: AddressTypeInfo | null;
   @Input() similarity: { score: number, match: AddressMatch, group: number } | null;
 
+  min = Math.min;
+
   groupColors: string[] = [
     'var(--primary)',
     'var(--success)',
```
