### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) header is not covered by the HMAC signature, allowing cross-tenant replay of legitimately signed webhook payloads - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop` (and `topic`, `webhook_id`, `api_version`) values that the rest of the pipeline treats as authenticated, tenant-identifying facts are taken from HTTP headers that are **not** included in the signed content. This is the same class of bug as the reported "field acted on but not covered by the signature" inflation-attack pattern: the binding `HMAC(secret, signed_bytes) == HMAC(secret, verified_bytes)` holds, but the binding `shop_used_by_handler == shop_actually_authenticated_by_Shopify` does not.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the supplied `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw HTTP body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.), none of which participate in `to_signable_string`: [3](#0-2) 

`Registry.process` only checks the HMAC and then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler — it never checks that the `shop-domain` header is consistent with anything the HMAC covers: [4](#0-3) 

`WebhookMetadata.shop` is a plain `const` populated from that unauthenticated header and handed to the app-defined `WebhookHandler#handle`, which apps use to scope/route data to a specific tenant/session: [5](#0-4) 

Because `api_secret_key` is a single, per-app secret shared across every shop that installs the app (it is not shop-specific), any merchant who has installed the app can receive a legitimately-signed webhook body from Shopify for their own store, then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header to name a different, victim shop. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` builds a `WebhookMetadata` claiming the payload belongs to the victim shop. Any app logic that uses `data.shop` to select the tenant record to update (a common pattern, e.g. "look up shop by `data.shop`, then write `data.body` into that shop's DB record") ends up applying attacker-controlled data under a different tenant's identity — a cross-tenant data/integrity breach reachable by an unprivileged internet user who merely needs to be an app installer on some shop.

### Impact Explanation
This crosses a tenant boundary: an attacker with no more privilege than "merchant installed on Shop A" can make the library-level abstraction assert that a Shopify-signed payload originated from Shop B. Any application built on this gem's webhook API that trusts `WebhookMetadata#shop` for tenant routing (which is the documented/intended use of that field) can be manipulated into applying cross-tenant writes or invoking mandatory-compliance webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) against the wrong shop. This matches the "Critical – cross-tenant access" bucket in the rubric, since the identity binding broken is exactly a field (the shop identifier consumed by the handler) that is not covered by the HMAC that the gem uses as its sole authenticity check.

### Likelihood Explanation
Likelihood is bounded by needing (a) an app that exposes webhook processing to more than one tenant behind the same endpoint (the common SaaS embedded-app pattern this gem is built for) and (b) attacker control of at least one legitimately installed shop to obtain a real signed webhook body. Both preconditions are ordinary for any real Shopify app; no access token, `client_secret`, or privileged account is required — only the attacker's own, unprivileged merchant install, which is exactly the kind of "unprivileged internet user" boundary the scan targets.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content used by `HmacValidator`, or otherwise cryptographically bind them (e.g., HMAC over `shop|topic|webhook_id|api_version|raw_body`) so that `Registry.process`/`Request` cannot be fed a validly-signed body under a spoofed shop/topic. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted for tenant routing without an independent verification step (e.g., cross-checking against a known/expected shop for that endpoint).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `products/update`) so Shopify sends a real `raw_body` + valid `x-shopify-hmac-sha256` computed with the app's `api_secret_key`.
2. Attacker captures `(raw_body, hmac)`.
3. Attacker resends this exact body/HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches (unchanged), so `Registry.process` proceeds: [6](#0-5) 
5. The app's `WebhookHandler#handle` is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled>)`, and any tenant-scoped logic in the app acts on the victim shop's data using attacker-supplied content, despite Shopify never having sent anything to/about that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-24)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
