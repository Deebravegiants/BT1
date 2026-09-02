This confirms the finding: the webhook `shop` (and `topic`, `webhook_id`, `api_version`) are read purely from HTTP headers, and the HMAC signature only ever covers the raw body via `to_signable_string`.This confirms the full chain: `WebhookMetadata.shop` (the tenant identifier delivered to every app's handler) is populated straight from `request.shop`, which is a raw, unauthenticated header value, while `Utils::HmacValidator.validate` only checks the HMAC against `to_signable_string`, which is just `@raw_body`. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never part of the signed material.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`/`api_version`) values that the library hands to the app's `WebhookHandler` are read directly from HTTP headers that are excluded from the signed payload, so any request bearing a valid body/HMAC pair can claim to originate from an arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the signature exclusively against that string using the app's shared `api_secret_key` [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) with no cryptographic tie to the body or to each other [3](#0-2) .

`Registry.process` validates only the HMAC and then forwards `request.shop` (the unauthenticated header) into `WebhookMetadata`, which is passed to the app's handler as the tenant identity for that event [4](#0-3) . `WebhookMetadata.shop` is a plain struct field with no independent verification [5](#0-4) .

The broken identity binding, stated as an equality that fails to hold:
`shop_authenticated_by_hmac == shop_the_handler_acts_on`

The HMAC secret (`api_secret_key`/`client_secret`) is shared across every shop that installed the app — it is not shop-specific. Any shop that installs the app legitimately receives real Shopify webhooks, each carrying a body and a correctly computed HMAC for that body under the shared secret. Because the header carrying the shop identity (`shopify-shop-domain`) is excluded from the signed material, an attacker who controls one installed shop (or who can otherwise obtain any valid `(body, hmac)` pair for the shared secret) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different `shopify-shop-domain` header value naming a victim shop. `Registry.process` will pass HMAC validation (it never looks at the header) and hand the handler a `WebhookMetadata` claiming the victim shop, causing the app to execute tenant-scoped business logic (e.g., `shop/redact`, `customers/data_request`, order/fulfillment updates, deactivating features) against the wrong tenant.

### Impact Explanation
This is a cross-tenant boundary crossing: an actor authenticated as one shop can cause the app to process an event as if it belonged to a different shop, because the field the app relies on for tenant scoping is unauthenticated. Depending on what the hosting app's `WebhookHandler#handle` does with `data.shop` (e.g., look up and mutate that shop's stored records, cancel orders, redact/delete data for mandatory compliance topics), this can result in unauthorized cross-tenant data modification or disclosure driven entirely through this gem's own webhook-verification API.

### Likelihood Explanation
Requires only knowledge of one valid `(raw_body, hmac)` pair signed under the app's shared secret — trivially obtainable by any shop that has installed the app and receives its own legitimate webhooks — plus the ability to send an HTTP request with a forged `shopify-shop-domain` header to the app's public webhook endpoint. No access token, `api_secret_key` knowledge, or privileged account is needed; the header can be freely set by any unprivileged sender.

### Recommendation
Bind the shop identity to the verified payload instead of trusting the header: parse `shop`/`topic`/`webhook_id` from the JSON body when present (Shopify Admin webhook payloads and topic metadata are consistent with the signed body), or include the relevant headers in the HMAC-signable string so header tampering invalidates the signature. At minimum, `Registry.process` should cross-check the header-derived shop domain against a shop identifier embedded in (and covered by) the signed body before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with a valid `X-Shopify-Hmac-SHA256` header computed over the JSON body using the app's shared secret.
2. Attacker replays the exact same raw body and `X-Shopify-Hmac-SHA256` value to the app's webhook endpoint, but changes the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com` (and, if desired, `X-Shopify-Topic` to a different registered topic such as `shop/redact`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the body/HMAC pair is genuinely valid for the shared secret [7](#0-6) .
5. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, and the app performs its topic-specific logic against `victim-shop.myshopify.com`, even though that shop never sent this webhook and the payload was never signed for it.

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
