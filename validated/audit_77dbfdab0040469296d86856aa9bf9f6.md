This confirms the identity-binding break: the webhook `shop` (tenant identifier) is read from the `x-shopify-shop-domain` HTTP header, but the HMAC signature covers only the raw request body — the header is never included in the signed material.

## Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw body, then trusts the `shop` value taken from the `x-shopify-shop-domain` header to attribute the event to a tenant, even though that header is never part of the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC exclusively against that signable string using the app's `api_secret_key` [2](#0-1) . Meanwhile, `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , which is not part of `to_signable_string` and therefore not covered by the signature at all. `Registry.process` validates the HMAC and then immediately hands `request.shop` to the app's handler as the tenant identity for the event, with no additional binding check between `shop` and the signed body: [4](#0-3) .

This breaks the intended identity binding `shop authenticated == shop attributed to the event`. An attacker who can reach the app's webhook endpoint (which must accept unauthenticated POSTs from the public internet by design, since Shopify's IPs aren't pinned by this gem) can take a **legitimately-signed webhook body** for shop A (e.g., replay a previously captured webhook payload, or reuse the same body/topic Shopify sends for any shop where the payload format is shop-independent, such as `app/uninstalled` with an empty `{}` body as shown in the test fixtures) and simply change the `x-shopify-shop-domain` header to shop B's domain. Because the HMAC only signs `@raw_body`, this forged request passes `HmacValidator.validate` unchanged, and `Registry.process` dispatches it to the handler tagged as belonging to shop B via `WebhookMetadata.new(... shop: request.shop ...)` [5](#0-4) .

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem lets an attacker cause a webhook event to be processed under an arbitrary merchant/shop identity without ever knowing the app's `client_secret`, because the header carrying that identity is outside the HMAC's protection scope. Depending on the handler's logic (many apps key their tenant data lookups, GDPR redaction, or state transitions directly off `WebhookMetadata#shop`), this can lead to cross-tenant data corruption, unauthorized redaction/deletion of another merchant's data, or state confusion between tenants — all triggered by an unauthenticated internet request that only needs to reuse a shop-independent, previously observed valid signed body (e.g., empty-body topics like `app/uninstalled`, `shop/redact` test payload is `{}` as shown in `test/webhooks/registry_test.rb`) [6](#0-5) .

### Likelihood Explanation
Any topic whose body is empty or shop-independent (several Shopify webhook topics send `{}` or fixed-shape payloads) lets an attacker compute nothing extra — they only need one previously-observed valid `(body, hmac)` pair for any shop and can replay it with a different `shop-domain` header value pointed at a different, unrelated store. No secret material or privileged access is required, only network reachability to the app's public webhook endpoint, which is required to exist by design for Shopify to deliver webhooks.

### Recommendation
Bind the tenant identity to the signed material: derive/verify the shop from data that is inside the HMAC-protected payload (e.g., validate the JSON body contains fields consistent with the claimed shop, or require the host application to independently confirm the `shop-domain` header value corresponds to a store for which this webhook topic/id was actually registered) rather than trusting an unauthenticated header purely because the accompanying body happens to carry a valid HMAC. At minimum, document that `request.shop` is unauthenticated and must not be used as a sole tenant key by the host app, and consider including the shop domain (and/or `webhook_id`) in `to_signable_string` if Shopify's outbound webhook signature ever incorporates it.

### Proof of Concept
1. Capture (or construct) any valid webhook delivery with an empty/shop-independent body, e.g. `raw_body = "{}"` and the correct `hmac = OpenSSL::HMAC.digest(sha256, api_secret_key, "{}")`, as used in the test suite [7](#0-6) .
2. Send a POST to the app's webhook endpoint with headers:
   - `x-shopify-hmac-sha256`: the valid Base64 HMAC of `"{}"`
   - `x-shopify-topic`: `app/uninstalled` (or any registered topic whose body doesn't need to vary)
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com` (any shop the attacker wants to target, not their own)
3. `ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers)` and `ShopifyAPI::Webhooks::Registry.process(request)` will succeed HMAC validation (`Utils::HmacValidator.validate(request)` only checks `@raw_body`) [8](#0-7)  and invoke the registered handler with `shop: "victim-shop.myshopify.com"` [5](#0-4) , even though the attacker never authenticated as, or on behalf of, that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** test/webhooks/registry_test.rb (L280-299)
```ruby
        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)
```
