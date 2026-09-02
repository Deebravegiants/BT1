### Title
Webhook shop/topic identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body [1](#0-0)  , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed by the app's secret. However, the tenant-identifying `shop` value used downstream comes from the unsigned `shopify-shop-domain` (or `x-shopify-shop-domain`) HTTP header [2](#0-1) . `Registry.process` passes this header value straight into the handler as the tenant identifier without any additional binding to the signature [3](#0-2) .

### Finding Description
The identity binding that should hold is:
`HMAC-verified bytes == bytes the handler trusts for tenant attribution`

In reality:
- HMAC-verified bytes = `raw_body` only.
- Bytes the handler trusts for tenant attribution = `raw_body` **plus** the `shopify-shop-domain` and `shopify-topic` headers, which are never included in `to_signable_string`.

Because the app's `client_secret` (the HMAC key) is shared across every shop that installs the app, any merchant who installs the app receives genuine webhook deliveries for their own shop, each with a body and a valid HMAC. Since the HMAC only signs the body, that exact `(body, hmac)` pair remains valid no matter what `shopify-shop-domain` or `shopify-topic` header values are sent alongside it. `HmacValidator.validate(request)` [4](#0-3)  will accept the forged headers, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` and `topic` are attacker-controlled while the signature check passed [5](#0-4) .

### Impact Explanation
This breaks tenant isolation (a Critical-class impact per the cross-tenant-access category): a low-privilege actor who merely installs the app on their own shop can cause the host application to process a webhook as if it originated from an arbitrary victim shop domain and/or arbitrary topic, while the signature validation reports success. Depending on how the host app's webhook handlers use `shop`/`topic` (e.g., to look up/update per-tenant records, trigger uninstall/GDPR flows, or sync data), this can lead to cross-tenant data corruption or disclosure.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (the normal case): the attacker needs no secret material, TLS interception, or elevated privileges — only the ability to install the app on a shop they control (an "unprivileged internet user" action) and to replay an HTTP request with modified headers to the app's own public webhook endpoint.

### Recommendation
Bind the shop (and topic) values into the signed content, or otherwise verify them independently of the header before trusting them, e.g.:
- Reject/flag webhooks where `shop` isn't a shop this application instance is aware of/expects for that delivery, and
- Recommend/require consuming apps to include `shop` as part of the value passed to `to_signable_string`, or expose a variant of `HmacValidator.validate` that also authenticates header-derived identity fields, rather than relying solely on body-HMAC equality for full request authenticity.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers to receive a webhook (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook POST to the app's endpoint with headers:
   `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: <valid HMAC over raw body>`.
3. Attacker captures this request (trivial, it's their own traffic) and replays it to the same endpoint, only replacing the header `shopify-shop-domain` with `victim-shop.myshopify.com` (and/or `shopify-topic` to a more sensitive topic like `app/uninstalled` or `shop/redact`), keeping body and `shopify-hmac-sha256` unchanged.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the HMAC [6](#0-5) .
5. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` [5](#0-4) , causing the host app to act on data attributed to a shop the attacker does not control.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
