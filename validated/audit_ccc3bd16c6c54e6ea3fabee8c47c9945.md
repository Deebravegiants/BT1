### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) fields are trusted for dispatch without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string as the raw request body only, while the shop-identifying header (`shopify-shop-domain` / `x-shopify-shop-domain`) is read directly from unauthenticated HTTP headers and passed straight into the handler dispatch. Any request whose body/HMAC pair is valid for *some* shop will be accepted for *any* shop value the caller places in the header, because the shop is never bound into the signature that `Utils::HmacValidator` checks.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via: [1](#0-0) 

The HMAC check delegates to `Utils::HmacValidator.validate`, which computes the signature over `verifiable_query.to_signable_string` and compares it to the received HMAC: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns **only the raw body** — it excludes the shop domain, topic, api-version, and webhook-id: [3](#0-2) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cross-check against the HMAC-verified payload: [4](#0-3) 

These header-derived, unauthenticated values are then handed to the registered handler as the identity of the tenant the event belongs to: [1](#0-0) 

This breaks the intended identity binding: `HMAC-verified(body)` ≠ `shop-that-is-acted-on`. The signature proves "this body was HMAC'd with the app's secret for *some* webhook event," but it proves nothing about which shop that event belongs to. A merchant who has the same app installed on their own store (an ordinary, unprivileged action — no special credentials, tokens, or app secret required) can legitimately trigger a webhook for their own shop, capture the resulting `(raw_body, hmac)` pair (their own store's webhook deliveries are visible to them, e.g., via their own endpoint logs or a delivery proxy they control), and then POST that exact `raw_body` + `hmac` to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `topic`/`webhook-id`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` dispatches the handler with `shop: <victim-domain>` even though the event content actually originated from the attacker's own store.

### Impact Explanation
This is a cross-tenant identity-binding failure: the field the handler acts on (`shop`) is not the field the cryptographic check actually authenticates (`raw_body`). Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g., to look up/update per-shop records, sync inventory, or gate business logic), an attacker can cause the app to process attacker-controlled event data under a victim shop's identity — a cross-tenant access/confusion vector, consistent with the Critical impact bucket ("cross-tenant access").

### Likelihood Explanation
Medium: the attacker needs their own store with the target app installed (a normal, unprivileged step available to anyone who can install a Shopify app) and the ability to send an arbitrary raw HTTP request to the app's public webhook endpoint with a chosen `shop-domain` header — both requirements are met by an ordinary internet-reachable attacker without any of the excluded privileged materials (`api_secret_key`, access tokens, TLS interception, etc.).

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the verified body — e.g., include the shop domain in the signable string, or independently verify the shop against a value obtained through an authenticated channel (session/access-token lookup) rather than trusting the raw header. At minimum, document and enforce that `WebhookMetadata#shop` must never be treated as authenticated by the HMAC check performed in `Utils::HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target app on their own test shop `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., `orders/create`) on their own shop, causing Shopify to POST `raw_body` with header `x-shopify-hmac-sha256: H` and `x-shopify-shop-domain: attacker.myshopify.com` to the app's webhook endpoint.
3. Attacker captures `raw_body` and `H` (both visible to them as the owner of the receiving/proxying infrastructure, or via a delivery-inspection tool they control).
4. Attacker sends a new POST to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only, which still matches `H`, so validation passes.
6. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though the event never originated from `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
