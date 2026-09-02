### Title
Webhook `shop` (and `topic`/`webhook-id`) attribution is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable string as only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and attribute the webhook are taken straight from unauthenticated HTTP headers. `Registry.process` trusts these header-derived values when dispatching to the app's handler, breaking the equality `request.shop (used for tenant attribution) == request.shop (covered by HMAC)`.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is defined as: [1](#0-0) 
i.e. only `@raw_body`. Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from request headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` uses `Utils::HmacValidator.validate(request)` only to confirm the body wasn't tampered with, then unconditionally trusts the header-derived `topic` and `shop` to select the handler and build the metadata passed to the app's business logic: [3](#0-2) 

Because `shop` (and `topic`/`webhook_id`) are excluded from `to_signable_string`, an attacker who owns a legitimate Shopify shop can obtain a genuinely-signed webhook (valid HMAC over a body they substantially control, e.g. product/order field values) from Shopify for their own store, then resend that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to claim it originated from a different merchant. `HmacValidator.validate` still passes because it never inspects the header values, and `Registry.process`/`WebhookMetadata` will hand the app's handler a `shop` value that has no relationship to the actual signer of the payload.

### Impact Explanation
Apps built on this gem are expected to key persisted webhook data and session/tenant lookups by `WebhookMetadata#shop`, since that is the only tenant identifier the library exposes for webhook processing. Because that field is not bound to the HMAC, an attacker can inject attacker-controlled (via their own shop's real business data) webhook payloads under the identity of a different merchant, resulting in cross-tenant data corruption/injection in the app's per-shop pipeline — a cross-tenant access break of the binding "attributed shop == cryptographically verified shop."

### Likelihood Explanation
Exploitation only requires the attacker to control any shop that installs the app (a normal, low-privilege attacker capability) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed. The header-spoofing step is trivial once a valid `(body, hmac)` pair is obtained from a legitimate webhook delivery for the attacker's own shop.

### Recommendation
Include `shop-domain`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them to the body), or require callers to independently authenticate the shop association (e.g., via looked-up webhook subscription id) before trusting `WebhookMetadata#shop`/`#topic` for tenant-scoped processing.

### Proof of Concept
1. Attacker owns `attacker.myshopify.com` and installs the target app, enabling e.g. the `products/create` webhook.
2. Attacker creates a product with attacker-chosen field values, causing Shopify to POST a genuinely HMAC-signed webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: products/create`, and a body containing the attacker-chosen fields, signed with the real `api_secret_key`.
3. Attacker captures this `(raw_body, hmac)` pair and replays it to the same endpoint, but swaps the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13`) recomputes the HMAC over `raw_body` only and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) proceeds and invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled data>, ...)`, even though `victim.myshopify.com` never sent this webhook. [4](#0-3) [5](#0-4) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
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
