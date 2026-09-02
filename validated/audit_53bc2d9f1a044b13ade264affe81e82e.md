### Title
Webhook `shop` identity is not covered by HMAC signature, enabling cross-tenant spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `Utils::HmacValidator.validate` binds solely to the body bytes. [1](#0-0)  The `shop` value handed to the application's webhook handler comes from the `x-shopify-shop-domain` header, which is never part of the signed payload. [2](#0-1)  This breaks the identity equality: `shop authenticated by HMAC` != `shop delivered to WebhookMetadata.shop`, letting an attacker who controls one tenant relabel a validly-signed webhook as belonging to a different shop.

### Finding Description
`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the registered handler with `request.shop` as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value using `OpenSSL.secure_compare`: [4](#0-3) 

For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body`, and `hmac` is parsed from the `hmac-sha256` header — neither incorporates `shop-domain`, `topic`, or `webhook-id`: [5](#0-4) 

The app's `api_secret_key` used to compute/verify this HMAC is shared across every shop that installs the app (it is not shop-specific), which is why Shopify's webhook HMAC in this design is a body-integrity check only, not a tenant-authentication check. The gem then trusts the unauthenticated `shop-domain` header as the tenant identity and forwards it straight into `WebhookMetadata.shop`, which is a `T::Struct` field consumed directly by the host application's `WebhookHandler#handle`: [6](#0-5) 

Because the header is outside the HMAC's signed scope, any party that has legitimately received one valid `(body, hmac)` pair from Shopify (e.g., because they installed the app on their own shop and thus receive real webhooks for their own shop) can replay that same `body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value. `HmacValidator.validate` will still return `true` because it only re-derives the signature from `@raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the spoofed shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged user who has installed the app on shop A can cause the app to process a webhook payload while claiming shop B (or any other shop string) as the origin. If the host application uses `WebhookMetadata.shop` to look up/create sessions, gate multi-tenant state, or perform shop-scoped side effects (a documented and expected usage pattern per `docs/usage/webhooks.md`, though not in scope itself), this results in cross-tenant data confusion/injection — satisfying the "cross-tenant access" criterion for a Critical-impact finding under this gem's own webhook-processing code, since the vulnerable binding (`Request#to_signable_string`/`Request#shop`) lives entirely in `lib/shopify_api/webhooks/`.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that trusts `WebhookMetadata.shop` (the field this gem explicitly hands to handlers) without independent verification: the attacker needs no secrets, only the ability to (a) receive one legitimate webhook to their own shop (trivial — install the public app) and (b) POST an HTTP request to the app's public webhook callback URL with a doctored `shop-domain` header and the captured `body`/`hmac`. No `api_secret_key`, access token, or privileged access is required, satisfying the unprivileged-internet-user bar.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material — e.g. have `Request#to_signable_string` incorporate the shop-domain header, or have `HmacValidator`/`Registry.process` cross-check the header-derived `shop` against a value independently obtained via an authenticated channel — so that the value exposed as `WebhookMetadata.shop` is provably the same value the HMAC actually authenticated.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and lets Shopify deliver one real webhook: captures `raw_body` B and the resulting valid `x-shopify-hmac-sha256` header H (computed by Shopify with the app's shared `api_secret_key`).
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body B and header H, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` object; `shop` returns `"victim.myshopify.com"` from the header. [2](#0-1) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the signature only from `B` and matches H, returning `true`. [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the application to process attacker-controlled data as if it originated from the victim shop. [8](#0-7)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
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
