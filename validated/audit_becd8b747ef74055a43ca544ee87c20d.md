### Title
Webhook `shop` domain is trusted from an unauthenticated HTTP header while only the raw body is HMAC-verified, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable representation of an inbound webhook using **only the raw request body**, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never part of the signed material. `Registry.process` validates the HMAC and, if it passes, hands `request.shop` (the unauthenticated header) directly to the app's `WebhookHandler` as ground truth for which tenant the payload belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers without any cryptographic binding to the body or to each other: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. against the body alone: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then forwards the **unauthenticated** `request.shop` header straight into `WebhookMetadata`, which the host app's handler treats as the identity of the tenant the payload came from: [4](#0-3) [5](#0-4) 

The identity binding that should hold is:
`HMAC-authenticated tenant == tenant the handler acts on (data.shop)`

But the gem only proves `HMAC-authenticated bytes == raw_body`; it does **not** prove `header shop-domain == the shop that produced this body`. Because the webhook secret (`api_secret_key`) is the app's single shared secret across every installed shop (there is no per-shop signing key — webhooks are keyed off the app's own client secret, not per-tenant), any body signed with a valid HMAC for one installation is a valid HMAC for *any* `shop` header value. An unprivileged internet user who can trigger one legitimate webhook delivery for a shop they control (e.g., installing the app on their own free/dev store and triggering `orders/create`) obtains a `(raw_body, hmac)` pair that is valid for that body forever. They can then POST that exact body/HMAC pair to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) with a victim shop's domain that is already installed on the app (guessable, since myshopify.com domains are enumerable/public). `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` dispatches `data.shop == victim-shop.myshopify.com` with attacker-controlled `data.body` to the handler.

### Impact Explanation
Downstream apps use `data.shop` from `WebhookMetadata` (per the gem's own documented usage pattern) to look up the corresponding merchant session/access token and to key persisted state (e.g., "queue background job for shop X with payload Y", or "update local order record for shop X"). Spoofing this field lets an unprivileged attacker inject attacker-controlled webhook payloads that are processed *as if they came from a specific victim tenant*, without ever needing that tenant's credentials. Depending on how the host app's handler uses `data.body` in combination with the victim's stored access token/session (a pattern this gem explicitly documents and expects), this enables cross-tenant data corruption or triggering of privileged actions performed with the victim shop's access token — meeting the "cross-tenant access" bar for this scan, since the tenant boundary (`shop`) that the whole webhook/session model relies on is not authenticated.

### Likelihood Explanation
High. No credentials, tokens, or `api_secret_key` are needed. The attacker only needs (a) the ability to trigger one legitimate webhook to their own shop (trivial — install the app on a free dev store or partner test store, a normal, unprivileged action), and (b) knowledge of a target `myshopify.com` domain, which is generally discoverable/public. The webhook endpoint is by design a public, unauthenticated internet-facing HTTP endpoint.

### Recommendation
Bind the tenant/topic identity into the signed material, or otherwise cryptographically tie the header claims to the verified payload. At minimum:
- Extend `to_signable_string` (or add a distinct verification step) so that `shop`, `topic`, and `webhook_id` are validated against Shopify's known delivery guarantees rather than trusted as raw headers, and/or
- Require host applications to independently confirm that `data.shop` corresponds to a shop for which this exact `webhook_id`/delivery was expected (e.g., cross-check against Shopify's Admin API or an idempotency/webhook-id ledger keyed by shop), and
- Document prominently that the `shop` header is **not** covered by the HMAC and must not be used as the sole tenant identifier for authorization-sensitive operations.

### Proof of Concept
1. Install the target app on an attacker-controlled `attacker-shop.myshopify.com` and register an `orders/create` webhook.
2. Trigger the webhook (e.g., create an order) and capture the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the app's `api_secret_key` over `B`).
3. Replay the exact same request to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, keeping body `B` and HMAC header `H` unchanged.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header; `Utils::HmacValidator.validate` succeeds because it only checks `H` against `B`.
5. `ShopifyAPI::Webhooks::Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` to the app's handler, which processes attacker-controlled data under the victim tenant's identity. [6](#0-5) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-73)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end

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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
    end
  end
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
