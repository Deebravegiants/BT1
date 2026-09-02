## Finding

### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw body only, while the `shop`, `topic`, and `webhook_id` values used by the rest of the library to dispatch and process the webhook are taken from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop`, `Request#topic`, and `Request#webhook_id` are read straight from HTTP headers with no cryptographic binding to that signature: [2](#0-1) 

`Registry.process` validates only the body via `Utils::HmacValidator.validate(request)`, and then dispatches to the app-registered handler using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

`HmacValidator.validate_signature` computes the digest strictly from `verifiable_query.to_signable_string` (i.e., only the body) against the app's single, shop-independent `Context.api_secret_key`: [4](#0-3) 

Because the `client_secret`/`api_secret_key` is one value shared by the app across every installed shop (it is not shop-specific), any tenant that installs the app can legitimately receive a genuine `(body, hmac)` pair from Shopify for their own shop. Since `shop-domain` is excluded from the signed content, that same valid `(body, hmac)` pair can be replayed to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header. The library will accept it as authentic (HMAC check passes) and hand the forged `shop` value to the host application's webhook handler via `WebhookMetadata`, breaking the identity binding: `shop authenticated (HMAC-covered bytes) == shop the handler acts on (header value)`.

### Impact Explanation
This lets an unprivileged internet user (any merchant who can install the app once, or anyone who captures one genuine webhook delivery) forge webhook events that the host application will attribute to a different, arbitrary shop. Depending on how the host app's webhook handler uses `data.shop` (e.g., to look up sessions, trigger `customers/redact`, `shop/redact`, or app-uninstall side effects, or to gate access to another tenant's data), this enables cross-tenant confusion/impact — the class of issue explicitly in scope (cross-tenant access via a broken identity binding).

### Likelihood Explanation
Moderate-to-high: only requires the attacker to control one shop where the app is installed (trivial — installing a Shopify app on your own dev/test store is unprivileged) and to be able to POST arbitrary headers to the app's public webhook endpoint, both of which are available to any internet user without any secret, token, or privileged access.

### Recommendation
Include `shop-domain`, `topic`, and `webhook_id` in the HMAC-signable content (or otherwise cryptographically bind them, e.g., have `Registry.process` cross-check the header `shop` against a shop already known/authorized to the app before dispatch), so that any tampering with these header values invalidates the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering Shopify to send a genuine webhook: body `B`, valid `hmac-sha256: H` (computed over `B` with the app's `client_secret`).
2. Attacker replays this exact HTTP request to the app's webhook endpoint but overwrites `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally a topic of their choosing, e.g. `customers/redact` if body content permits) while leaving `B` and `H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — signature still matches. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the signed payload was never associated with that shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
