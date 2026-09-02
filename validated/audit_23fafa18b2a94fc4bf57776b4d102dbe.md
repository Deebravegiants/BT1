## Title
Webhook shop-domain and metadata headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body signature and then hands the header-derived `shop` value straight to the app's webhook handler as the tenant identity. This breaks the intended binding `shop-authenticated-by-HMAC == shop-used-as-tenant-key`, letting an attacker who controls any one legitimately-signed webhook body attribute it to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers that are never part of the signed material: [2](#0-1) 

`HmacValidator.validate` (used by `Registry.process`) only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac-sha256` header value; it never touches the other headers: [3](#0-2) 

`Registry.process` then trusts `request.shop` (and `request.topic`/`request.webhook_id`/`request.api_version`) as the authenticated tenant context passed to the app's handler, with no cross-check against the body or any known-installed-shop list: [4](#0-3) 

Because Shopify signs the *body* with the app's shared `client_secret` (identical across every shop using the app), any shop that has the app installed can capture one of its own legitimately-signed webhook deliveries (valid `hmac-sha256` over that raw body). Since the signature says nothing about which shop it came from, that same `(raw_body, hmac)` pair remains cryptographically valid when replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a different (victim) shop's domain. `Registry.process` will accept it as valid — `Utils::HmacValidator.validate` only checks the body/HMAC pair — and will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain and `WebhookMetadata#body` set to attacker-controlled content.

This is the same bug class as the report: a field the code *acts on* (`shop`, used as the tenant/session key for the webhook event) is not part of the value that is cryptographically *verified* (only `raw_body` is HMAC-covered). The equality that should hold — `shop_verified_by_hmac == shop_used_as_tenant_key` — does not hold, because `shop` is read from an unauthenticated header entirely outside the signed scope.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` to scope tenant data (e.g., "which merchant does this order/customer/app-uninstalled event belong to") can be fed forged, cross-tenant webhook events by an attacker who merely has their own (unrelated) shop's webhook payload and a way to replay HTTP requests to the app's public webhook endpoint. This is a cross-tenant access vector: data or events legitimately signed for shop A can be injected into shop B's tenant context, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The webhook receiving endpoint is, by design, a public HTTP endpoint (it must be reachable by Shopify's servers), so no credentials are needed to send a request to it. Obtaining a validly HMAC-signed body only requires access to one's own shop's webhook deliveries (e.g., by installing the app on an attacker-controlled shop, or capturing any webhook payload whose HMAC remains valid regardless of the `shop-domain` header). No secret key, access token, or privileged account is required — only unprivileged replay of a byte-for-byte body/HMAC pair with a modified header.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material that is verified — either by including these values in the signable string used for HMAC validation, or by having `Registry.process`/the consuming application separately validate `request.shop` against a known, previously-authenticated shop for that specific webhook subscription before invoking the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host application against its own session store before being trusted as a tenant key.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com` and trigger any webhook topic the app has registered (e.g. `orders/create`). Capture the raw HTTP request Shopify sends to the app's webhook endpoint, including `raw_body` and the `X-Shopify-Hmac-Sha256` header.
2. Replay this exact request to the same webhook endpoint, but change the `X-Shopify-Shop-Domain` header to `victim.myshopify.com` (leaving `raw_body` and `X-Shopify-Hmac-Sha256` untouched).
3. `ShopifyAPI::Webhooks::Request.new` parses the modified headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC of `raw_body` only and finds it matches — validation passes. [5](#0-4) 
4. The registered handler is invoked with `WebhookMetadata.shop == "victim.myshopify.com"` and attacker-controlled `body`, even though the signature never certified any relationship between that body and `victim.myshopify.com`.

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
