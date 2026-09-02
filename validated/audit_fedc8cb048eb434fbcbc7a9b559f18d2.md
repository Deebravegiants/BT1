### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant spoofing of `WebhookMetadata.shop` - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the unauthenticated `shopify-shop-domain` (or `x-shopify-shop-domain`) header as the tenant identifier passed to the app's handler. Because the header is not part of the signed payload, an attacker who controls any legitimate installation of the app (any merchant who installs the app, including via a free dev store) can produce a validly-HMAC-signed request and then swap the shop-domain header to any victim shop, causing the host application to process attacker-controlled webhook data under a different tenant's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` uses this validation as the sole authentication gate, then reads `request.shop` (from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in `to_signable_string`) and forwards it to the app's handler as the trusted tenant identifier: [3](#0-2) [4](#0-3) 

Since the same `api_secret_key` is shared across all shops that install the app, and since the gem's own documentation instructs developers that calling `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook" (implying it is a trustworthy, verified identity), an attacker with a legitimate install of the app (any account, including a free dev store) can:
1. Trigger any webhook topic on their own store to obtain a body + valid `X-Shopify-Hmac-Sha256` signed with the app's shared secret.
2. Replay that exact `raw_body`/HMAC pair directly to the app's public webhook endpoint, but with the `shopify-shop-domain` header changed to a victim shop's domain.

Because HMAC validation only covers the body, the signature still validates, and `WebhookMetadata.shop` will report the victim's domain even though the payload actually originated from the attacker's own store. This breaks the identity binding: `shop-header-that-drives-tenant-lookup == shop-that-actually-authenticated-the-request` is false after the attack, matching the "shop authenticated vs shop used as identity/session key" and "field acted on but not covered by the HMAC" analog classes.

Root cause: `to_signable_string` in `lib/shopify_api/webhooks/request.rb` (lines 35-38) never incorporates `shop`, `topic`, or `webhook_id` header values into the signed material, while `Registry#process` (lines 188-199) still treats `request.shop` as validated/tenant-authoritative once `HmacValidator.validate` passes.

### Impact Explanation
This qualifies as High severity: cross-tenant access. Any application built on this gem's documented pattern (per `docs/usage/webhooks.md`) that uses `data.shop` from a processed webhook to look up per-tenant records, credentials, or to perform tenant-scoped writes (the exact intended usage shown in the gem's own docs, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-supplied payload content while believing it originated from a different (victim) merchant's shop. This can lead to data corruption, unauthorized state changes, or information disclosure across tenant boundaries in applications built directly per this gem's guidance — without any privileged credentials being required from the attacker, only a legitimate low-privilege app install (e.g. a free development store).

### Likelihood Explanation
Likelihood is high for any app that exposes its webhook endpoint publicly, as required by Shopify's model (the documented example in `docs/usage/webhooks.md` shows a plain public Rails route). Obtaining a legitimate, validly-signed webhook body only requires installing the target app on any shop, which is typically self-serve/free. No secret material beyond what the attacker's own installation already legitimately receives is needed, and no interception of the app's `client_secret` is required.

### Recommendation
Bind the tenant/shop identity into the HMAC-verified surface, or otherwise cryptographically bind the shop-domain header to the request signature, before trusting it. Concretely:
- Include `shop`, `topic`, and `webhook_id` header values in the signable/verified material for webhook requests (or verify that the recorded shop for a given webhook subscription/topic matches an app-side registration authenticated separately), instead of relying on an unauthenticated header purely for HMAC-of-body verification.
- At minimum, update documentation to explicitly warn that `data.shop` is not covered by the Shopify webhook HMAC and must not be treated as an authenticated tenant identifier by itself; recommend that consuming applications cross-check `data.shop` against known/registered shops for that specific webhook subscription (e.g., by including a shop-scoped, unguessable path/secret per subscription) rather than trusting the header value directly.

### Proof of Concept
1. Merchant Mallory installs the vulnerable app on her own store `mallory-shop.myshopify.com` and triggers a subscribed webhook topic (e.g. `orders/create`), causing Shopify to POST a validly HMAC-signed request to the app's public webhook endpoint (`https://victim-app.com/webhooks`) with headers:
   - `X-Shopify-Hmac-Sha256: <valid signature of raw_body over api_secret_key>`
   - `X-Shopify-Shop-Domain: mallory-shop.myshopify.com`
2. Mallory intercepts/replays this same request (same `raw_body`, same HMAC header) directly to the app's public webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` (`Request#to_signable_string`) — validation passes because the body/signature pair is untouched. [3](#0-2) 
4. The app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes Mallory's payload as if it came from the victim shop, per the documented handler pattern in `docs/usage/webhooks.md` (lines 19-29).

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
