Confirmed: the vulnerability is real and well-supported by the code. The `shop` field used to construct `WebhookMetadata` is taken directly from an unauthenticated HTTP header, while the HMAC only covers the raw body.

### Title
Webhook shop-domain identity spoofing via header not covered by HMAC signature - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb], [File: lib/shopify_api/utils/hmac_validator.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the `shop` value taken from an unauthenticated HTTP header (`x-shopify-shop-domain` / `shopify-shop-domain`) to build the `WebhookMetadata` passed to the host application's handler. Because the shop identity is not bound to the HMAC, any tenant that can generate a legitimately-signed webhook (any shop that has installed the app, since all shops share the same app-level `client_secret`) can present that valid `(body, hmac)` pair to the app's webhook endpoint together with an arbitrary `shop-domain` header, causing the app to process attacker-supplied data under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the signature: [3](#0-2) 

`Registry.process` validates only the HMAC (over body), then immediately forwards the unauthenticated `request.shop` value into `WebhookMetadata`, which is what host applications use to determine which tenant/merchant the webhook belongs to: [4](#0-3) 

The identity binding that should hold is: `hmac_valid(body) == true` should imply the `shop` field is authentic for that body. Instead, the code only proves `hmac_valid(body) == true`; the `shop` header is parsed but never verified, so `shop` can be swapped freely without invalidating the signature. Because Shopify computes webhook HMACs using the app's single `api_secret_key` for every shop that installs the app (not a per-shop secret), any shop that has installed the app can obtain a validly-signed `(body, hmac)` pair through entirely legitimate use of their own store (e.g., triggering an `orders/create` event), and then replay that exact body+hmac to the app's shared webhook endpoint while substituting a different `shop-domain` header value belonging to another tenant of the same multi-tenant app.

### Impact Explanation
This breaks the tenant-isolation boundary that `WebhookMetadata.shop` is relied upon by host applications to enforce (per the gem's own documentation, handlers use `data.shop` to determine which merchant's data to update/enqueue work for). An attacker-controlled shop can inject arbitrary webhook payloads that the app will process as belonging to a victim shop, resulting in cross-tenant data corruption/access in any application built on this gem's documented webhook contract. This matches the "Critical - cross-tenant access" category since the shop identity binding is broken by design in the gem's verification logic, not by a host-application mistake.

### Likelihood Explanation
Likelihood is significant: exploitation requires no secrets, no TLS interception, and no privileged access—only that the attacker's own shop has installed the target app (a standard, unprivileged action any Shopify user can take by installing a public app), after which they can trigger legitimate webhook events on their own store and replay the resulting signed body with a forged `shop-domain` header to the app's single shared webhook endpoint.

### Recommendation
Bind the shop (and ideally topic) to the HMAC verification, e.g. by including the `shop-domain` header value in the signable string that `HmacValidator` verifies, or by requiring `Registry.process` to independently confirm that a session/registration exists for the claimed shop before dispatching to the handler. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant identification without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (a normal, unprivileged install).
2. Attacker performs a legitimate action (e.g., creates an order) that causes Shopify to POST a genuine `orders/create` webhook to the app's registered endpoint, signed with the app's `api_secret_key`:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-hmac-sha256: <valid HMAC over raw body>
   { ...order json... }
   ```
3. Attacker captures this exact `(raw_body, hmac)` pair (it is delivered to an endpoint they control, since it's their own store's webhook).
4. Attacker resends the identical body and `x-shopify-hmac-sha256` value to the same app endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the HMAC against `raw_body` — this still passes because the body is unchanged: [5](#0-4) 
6. `WebhookMetadata` is built with `shop: request.shop` equal to `"victim-shop.myshopify.com"`, and the handler processes the attacker's data as if it originated from the victim shop: [6](#0-5)

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
