### Title
Webhook shop/topic identity spoofing via replay — HMAC covers only the raw body, not the `shop-domain`/`topic`/`webhook-id` headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying that `hmac-sha256` matches an HMAC of the raw request **body**. The `shop-domain`, `topic`, `api-version` and `webhook-id` headers — which the handler trusts as the identity/context of the event — are not part of the signed material at all. Any party capable of obtaining one legitimately-signed webhook (i.e. any merchant who installs the app on their own store, a self-service, unprivileged action) can replay the same body+HMAC pair while swapping the `shop-domain` header to a victim shop, causing the host app's handler to process attacker-controlled data as if it came from a different, victim tenant.

### Finding Description
The equality the gem is supposed to enforce is:

`shop that produced/authenticated the payload == shop the handler is told the payload came from`

In `Utils::HmacValidator.validate`, the only verified material is `verifiable_query.to_signable_string`: [1](#0-0) 

For a webhook `Request`, `to_signable_string` returns just `@raw_body` — nothing else: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated headers: [3](#0-2) 

`Registry.process` validates the HMAC (body-only) and then unconditionally forwards these unauthenticated header values to the handler as the trusted identity of the event: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is the app's single client secret shared across **every** shop that has the app installed, any user can self-install the app on their own shop, trigger a webhook, and legitimately receive a valid `(raw_body, hmac)` pair. That exact pair remains valid forever for that specific body content — nothing binds it to the `shop-domain` header, the `topic` header, or a timestamp/nonce. The attacker can then POST the identical body+HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to the victim's domain (and/or `topic`/`webhook-id` changed), and `HmacValidator.validate` will still return `true`, because it only ever checks the body.

The two request headers `shop-domain` and `topic` are not idempotent or invariant to protocol-level replay: `Utils::HmacValidator.validate` proves body integrity, but `Registry.process` conflates that body-integrity check with "this event, with these headers, came from this shop" — an equality that is never actually checked anywhere in the code path.

### Impact Explanation
This breaks the cross-tenant boundary the gem is meant to provide to the host application: the `WebhookMetadata` handed to `handler.handle` claims a `shop` that has no cryptographic binding to the verified payload. A host app that stores/updates per-shop data keyed by `data.shop` (the intended and only way to consume this API) can have its data model poisoned with attacker-supplied content attributed to an arbitrary victim shop domain, or have shop-specific business logic (uninstall/redact handling, order sync, etc.) triggered for a shop the attacker does not control. This matches the "Critical - cross-tenant access" category, since the attacker fully controls both the webhook body (via their own installation) and now the shop identity attributed to it, entirely from their own unprivileged capacity.

### Likelihood Explanation
Likelihood is high because:
- No credentials, `api_secret_key`, access tokens, or privileged access are required — only self-service app installation on a shop the attacker controls, which is inherent to how Shopify apps work.
- The attacker obtains a fully valid signature "for free" simply by receiving any webhook to their own store.
- Replaying an HTTP POST with modified headers requires no special tooling.
- The vulnerability is a structural gap in what the library treats as "verified" versus what it hands to the caller as trusted context, not a misuse of a documented API by the host app — the host app is doing exactly what the gem's docs instruct (consume `WebhookMetadata#shop` from a processed, HMAC-"validated" request).

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie the webhook body to the shop/topic before trusting them:
- Have `Utils::HmacValidator`/`Webhooks::Request#to_signable_string` incorporate `shop`, `topic`, and `webhook_id` (or otherwise cross-check them) rather than signing the body alone, if Shopify's signing scheme permits an extended canonical string.
- At minimum, document loudly that `WebhookMetadata#shop`/`#topic` are unauthenticated header values that must be independently correlated (e.g., against a known/installed-shop list, or against `body["domain"]`/similar first-party fields inside the signed JSON body) before being trusted for any per-tenant operation, and add such a cross-check inside `Registry.process` (e.g., reject if `request.shop` does not match a shop domain embedded in the parsed body, when available).
- Consider adding replay protection (nonce/timestamp binding) since the HMAC covers a static body with no freshness guarantee.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, unprivileged).
2. Attacker triggers any registered webhook topic (e.g., `orders/create`) on their own shop, capturing the raw POST: headers include `x-shopify-hmac-sha256: <H>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, body `B`.
3. `Utils::HmacValidator.validate` for this request computes `HMAC-SHA256(api_secret_key, B) == H` → true (legitimate, since it is their own shop and the shared app secret).
4. Attacker replays the exact same `B` and `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `topic`/`webhook-id`), and POSTs to the app's webhook endpoint.
5. `Utils::HmacValidator.validate` still returns `true` (it only checks `B` against `H`), and `Registry.process` invokes the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e. the app now believes attacker-controlled order data belongs to `victim-shop.myshopify.com`. [4](#0-3) [5](#0-4)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L1-38)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
