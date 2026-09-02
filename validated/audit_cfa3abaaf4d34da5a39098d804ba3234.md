### Title
Webhook tenant identity (`shop`, `topic`, `webhook_id`, `api_version`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` in `ShopifyAPI::Webhooks::Registry.process` only authenticates the JSON body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from unauthenticated HTTP headers and passed straight into `WebhookMetadata`/`handler.handle` with no cryptographic binding to the signed body. This breaks the identity equality that should hold: `shop_bound_by_hmac == shop_acted_on_by_handler`.

### Finding Description
`Request#to_signable_string` signs only the raw body: [1](#0-0) 

The tenant-identifying fields are extracted from headers, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then forwards the header-derived, unauthenticated `shop`/`topic`/`webhook_id`/`api_version` values to the application's handler as trusted metadata: [3](#0-2) 

`WebhookMetadata` treats `shop` as an authoritative field the handler acts on to attribute the event to a tenant: [4](#0-3) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e., in this case the raw body bytes, and never incorporates the headers: [5](#0-4) 

Because Shopify (and the HMAC check) only vouches for the *body*, not the `shop-domain`/`topic`/`webhook-id` headers, any party who can influence or replay the headers reaching the app's webhook endpoint (e.g., a reverse proxy misconfiguration, a shared endpoint receiving webhooks for multiple shops, or replay of a previously captured valid `(body, hmac)` pair with a substituted `X-Shopify-Shop-Domain` header) can make the app process the event as belonging to a different shop than the one Shopify actually attributed it to. This is directly analogous to the reported CREATE/CREATE2 bug: a check exists (`HmacValidator.validate`) but the field that business logic actually acts on (`shop`) is not covered by what the check verifies (`raw_body`), so the "authentication" silently does not bind to the value being trusted downstream.

### Impact Explanation
This breaks the equality `shop_verified_by_signature == shop_used_for_tenant_attribution`. An attacker who can deliver a request with a valid `(raw_body, hmac)` pair (for instance from their own shop's genuine webhook, or any body whose HMAC they can obtain) but an arbitrary `shop-domain` header, can cause the app to execute webhook handler logic (order/customer/product events, GDPR `customers/redact`, `shop/redact`, `customers/data_request`, etc.) while attributing the payload to a victim shop. Depending on how the host application keys per-tenant data/authorization off `WebhookMetadata#shop`, this enables cross-tenant data injection or corruption — qualifying as cross-tenant access under the Critical impact category.

### Likelihood Explanation
Exploitability depends on whether an attacker can influence the headers of the HTTP request reaching the app's webhook processing code independent of the signed body — e.g., via a shared/multi-tenant ingress, a proxy that doesn't lock the shop header to the TLS/connection origin, or replay of a previously observed valid body+HMAC. The gem itself provides no defense-in-depth here since it never binds `shop`/`topic`/`webhook_id` to the signature, so any deployment that doesn't independently pin the shop header to the request origin is exposed. This differs from the OAuth flow, where `AuthQuery#to_signable_string` does include `shop`, `host`, `state`, `code`, `timestamp` in the signed material — the webhook path is the outlier that omits identity fields from the signature.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the material that `HmacValidator` verifies (or otherwise cryptographically bind them to the signed body), or require the host application to independently authenticate the `shop-domain` header against the connection/session before trusting `WebhookMetadata#shop`. At minimum, document clearly that `shop`, `topic`, and `webhook_id` are unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on a shop they own (`attacker-shop.myshopify.com`), or otherwise obtains a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair for some webhook topic the app is registered for.
2. Attacker replays that exact `raw_body` and `hmac` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present). [6](#0-5) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the secret — it never inspects `shop`. [7](#0-6) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the body/HMAC was originally generated by Shopify for `attacker-shop.myshopify.com`, causing the app to process/attribute the event under the wrong tenant. [8](#0-7)

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
