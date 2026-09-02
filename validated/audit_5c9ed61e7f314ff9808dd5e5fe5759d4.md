Confirmed: `Registry.process` extracts `request.shop` directly from the header and passes it to the handler as the tenant identifier, while `Request#to_signable_string` only returns `@raw_body`, so the HMAC never covers the shop-domain header at all.### Title
Webhook shop identity spoofing — HMAC signs only the raw body, not the `shop-domain` header used for tenant attribution - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `X-Shopify-Shop-Domain` header — which is never part of the signed material — to attribute the event to a tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, independent of the signed body: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop` from the (unsigned) header, handing it to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The broken identity binding is:
```
shop attributed to the event (WebhookMetadata#shop, from header)
   ≠
shop actually authenticated by the HMAC (only the raw body bytes)
```

Since the app's `client_secret` is the same secret used for every shop's webhooks, an attacker who legitimately installs the app on their own store (an unprivileged, non-credentialed action) receives real webhook deliveries with a valid HMAC computed over a body they fully control the shape of for many topics (e.g. `orders/create`, `products/update`, `carts/update`), for which the body does not itself encode the sending shop's domain. The attacker can then replay that exact `raw_body` + valid `hmac-sha256` value to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the victim's domain, causing the host application to process attacker-supplied data as if it originated from the victim tenant.

### Impact Explanation
This is a cross-tenant attribution bypass: an attacker with no credentials for a victim shop can make the app process arbitrary attacker-chosen webhook payloads under the victim's shop identity, directly matching the Critical "cross-tenant access" category, since any host application that keys webhook side effects (order sync, inventory updates, redact/GDPR flows, uninstall handling for mandatory topics, etc.) off `WebhookMetadata#shop` will act on the wrong tenant's data.

### Likelihood Explanation
Moderate-to-high. The attacker only needs to install the app on their own store (no special privilege), capture one legitimate webhook delivery with its `hmac-sha256` header, and replay it with a modified `shop-domain` header. No possession of the `client_secret` or any victim credential is required, and the flaw sits entirely in this gem's `Registry.process`/`Request` classes rather than in host-application misuse.

### Recommendation
Bind the shop (and topic/webhook id) into the value that is HMAC-verified, or cross-check the header-derived shop against an independently authenticated source (e.g. a per-shop webhook signing check, or requiring the caller to additionally prove shop identity via a previously issued, shop-bound secret/session) before trusting `WebhookMetadata#shop`. At minimum, document/require that host apps validate the delivered shop against an installed-shop record rather than trusting the header value as authenticated by the HMAC.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`, which is a valid tenant of the app.
2. App receives a legitimate `orders/create` webhook for `attacker.myshopify.com`:
   - Headers: `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`
   - Body: attacker-controlled order JSON (attacker can create arbitrary orders/products in their own store to control the body).
3. Attacker captures `raw_body` and the corresponding `hmac-sha256` value.
4. Attacker sends a new HTTP request to the same webhook endpoint with the identical `raw_body` and `hmac-sha256`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the secret [6](#0-5) .
6. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, causing the host app to treat attacker data as belonging to `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
