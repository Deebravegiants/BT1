Confirmed. `Registry.process` validates the HMAC against `request.to_signable_string`, which returns only `@raw_body` [1](#0-0) , then unconditionally trusts `request.topic` and `request.shop` — both parsed straight from unauthenticated headers [2](#0-1)  — and passes them into the handler as the tenant identity [3](#0-2) .

### Title
Webhook `shop`/`topic` headers are trusted without being covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then unconditionally trusts the `shop-domain` and `topic` headers when constructing the `WebhookMetadata` handed to the app's handler. Because the HMAC signature is computed over the body only, the shop identity is not cryptographically bound to the request.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over exactly that signable string and compares it to the `hmac` reader, which itself is parsed from the `hmac-sha256` header: [4](#0-3) [5](#0-4) 

The `shop`, `topic`, `api_version`, and `webhook_id` fields are all read from separate, unauthenticated headers with no cryptographic relationship to the body or the HMAC: [6](#0-5) 

`Registry.process` validates the HMAC, then immediately trusts `request.shop` and `request.topic` to build the `WebhookMetadata` object dispatched to the app-provided handler, which apps use to determine which merchant's data the payload belongs to (per the gem's own documented handler contract: `data.shop`, `data.topic`, `data.body`): [3](#0-2) [7](#0-6) 

This is the exact bug-class pointed to in the report: a field (`shop`) that a downstream consumer acts on as an identity/tenant selector is not covered by the message authentication code that gates trust in the request. Equality that should hold but doesn't: `shop bound by HMAC == shop acted upon by handler`. Here, `shop acted upon by handler = header value (unauthenticated)`, while `shop bound by HMAC = ∅` (nothing — only the body bytes are signed).

### Impact Explanation
Any user who can install the app on their own store (an unprivileged internet user, in the sense that no privileged credential of the app or victim is required) can trigger a legitimate webhook delivery from their own shop, capturing a genuinely valid `(raw_body, hmac-sha256)` pair signed with the app's `client_secret` by Shopify. Because `shop-domain` (and `topic`) are not part of the signed material, the attacker can resend that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and even `X-Shopify-Topic`) with an arbitrary victim shop domain. The HMAC check still passes (body unchanged), and the app's handler will process/store the attacker's payload as though it belongs to the victim shop — a cross-tenant data injection into another merchant's session/records. This matches the Critical "cross-tenant access" impact category, since it lets one tenant's authenticated webhook traffic be attributed to and processed under a different tenant's identity.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (the normal SaaS model): an attacker only needs to be a legitimate, unprivileged merchant of the app to generate valid signed webhook bodies from their own store, then replay them with a forged shop header to any endpoint the app exposes for `Registry.process`. No access token, `client_secret`, or victim credential is required — only the ability to receive one's own webhook and re-POST it with a different header.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `api_version`, `webhook-id`) header values in the signable string used for HMAC validation, or otherwise cryptographically bind them to the verified payload (e.g., require the app to independently confirm the shop via a stored session/webhook subscription mapping keyed by `webhook_id` before trusting `request.shop`). At minimum, document that `request.shop`/`request.topic` are unauthenticated and must not be used as an identity/authorization boundary without additional verification.

### Proof of Concept
1. App has installed webhook handler for topic `orders/create`, registered via `Registry.add_registration`.
2. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers `orders/create`; Shopify posts a webhook with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's `client_secret`, plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `raw_body` and `hmac-sha256` header value.
4. Attacker re-sends the identical `raw_body` and `hmac-sha256` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC (`Request#to_signable_string` returns `@raw_body`, see `lib/shopify_api/webhooks/request.rb:35-38`).
6. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` with `shop == "victim.myshopify.com"` and dispatches it to the app's handler (`lib/shopify_api/webhooks/registry.rb:198-199`), which processes attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
