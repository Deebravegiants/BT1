### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) header not covered by the HMAC signature, allowing cross-tenant identity spoofing after HMAC validation passes - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` only signs the raw JSON body when computing the HMAC used to authenticate an inbound webhook, while `Registry.process` uses the unauthenticated `shop-domain` header as the tenant identifier handed to the app's webhook handler. The `shop` (and `topic`) claimed by the request is never bound to the HMAC that is verified, breaking the identity equality that the caller implicitly relies on: `verified_bytes == bytes_the_handler_trusts_as_the_tenant_identity`.

### Finding Description
`Registry.process` validates a webhook exclusively via: [1](#0-0) 

The HMAC validity check only guarantees the integrity of the raw body, because `Request#to_signable_string` returns `@raw_body` and nothing else: [2](#0-1) 

`HmacValidator.validate` computes/compares the signature strictly over `verifiable_query.to_signable_string`: [3](#0-2) 

Yet `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all read straight from attacker-controllable HTTP headers — are passed to the handler as authoritative metadata once the (body-only) HMAC check succeeds: [4](#0-3) 

Because Shopify signs webhooks for an app using the single, app-wide `api_secret_key` (not a per-shop secret), a valid `(raw_body, hmac)` pair produced for any shop that has the app installed remains a *valid* signature no matter which `shop-domain`/`topic`/`webhook-id` headers accompany it. `Request.new` never cross-checks these header values against anything covered by the signature — it only requires the headers to be *present*, not that they be *authentic*: [5](#0-4) 

This is exactly the bug class described in the reference report: a field that is *acted on* (the tenant/topic identity used by the handler to route/attribute the webhook) is not covered by the integrity check (the HMAC) that is supposed to authenticate the request.

### Impact Explanation
This breaks the binding `shop_verified_by_hmac == shop_used_by_handler`. Any host application that trusts `WebhookMetadata#shop` (or `#topic`) to look up per-tenant state, apply per-shop authorization, or attribute incoming data — the intended and documented usage of this field — can be made to process data under a different shop's identity or under a different topic than what Shopify actually signed, once an attacker possesses any one valid `(raw_body, hmac)` pair from the app's webhook stream (e.g., from their own installed instance of the app). This is a cross-tenant confusion vector consistent with the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to have obtained at least one legitimately-signed `(raw_body, hmac)` pair delivered under the shared app secret (e.g., by installing the app on their own store and observing/replaying webhook traffic reaching the app's public endpoint) and to replay it directly to the app's webhook endpoint with substituted `shop-domain`/`topic` headers. It does not require the `api_secret_key`, an access token, or TLS interception — only a body+HMAC pair that was already validly produced for the shared secret, which any merchant with the app installed can obtain from their own webhook traffic.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them, e.g. concatenate the raw headers with the raw body before hashing), matching what Shopify actually signs, so that `Registry.process` cannot be fed a validly-authenticated body paired with attacker-chosen identity headers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`; Shopify delivers a real webhook to the app with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures/replays this exact `(B, H)` pair directly to the app's public webhook endpoint, but substitutes `X-Shopify-Shop-Domain: victim.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the request because all three required headers are present.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` — it passes, since `B`/`H` are unmodified. [1](#0-0) 
5. The handler receives `WebhookMetadata` claiming `shop: "victim.myshopify.com"` with body content that actually originated from the attacker's own store, despite passing HMAC validation — a fully "verified" webhook whose tenant identity was never actually checked.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
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
