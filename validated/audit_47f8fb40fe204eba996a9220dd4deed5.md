### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook HMAC verification in this gem only authenticates the raw request body, while the `shop`, `topic`, and `webhook-id` values used downstream to identify the tenant and route the event are taken from unsigned HTTP headers. This breaks the intended identity binding: `hmac == HMAC(body)` is verified, but the code acts on `shop == header("shopify-shop-domain")`, a value that is never part of what the HMAC covers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic linkage to the signed payload: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then immediately trusts `request.shop` (and `request.topic`) to build the metadata handed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` confirms `computed_signature = HMAC(to_signable_string, secret)`, i.e. it authenticates only the byte string returned by `to_signable_string` (the body): [4](#0-3) 

Because the header fields are excluded from the signed string, the equality the code effectively (and incorrectly) relies on is:
`HMAC(body) valid ⇒ shop_header trustworthy`

when the real binding needed is `HMAC(body ∥ shop ∥ topic ∥ webhook_id) valid`. Any request whose body+HMAC pair is a byte-for-byte legitimate Shopify webhook (signed with the app's real `client_secret`) will pass validation regardless of what `shop`, `topic`, or `webhook-id` headers say, since none of those are part of the signed material.

### Impact Explanation
An attacker who is a legitimate merchant with the app installed on their own store receives genuine Shopify webhooks for their own shop, each carrying a valid `X-Shopify-Hmac-Sha256` header computed with the app's real secret over the body. The attacker can capture one such body+HMAC pair and replay it to the app's public webhook endpoint while forging the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a different, victim shop. `Registry.process` will pass HMAC validation (the body+signature pair is authentic) and then dispatch `WebhookMetadata` claiming the event belongs to the victim shop's tenant. Any app handler that uses this `shop` value to select which tenant's data/session to mutate is fed a value with no authenticity guarantee, resulting in cross-tenant event injection — data believed to originate from and apply to one merchant can be attributed to and processed under another merchant's identity. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker control (or have installed) the app on any one shop to obtain a single authentic body+HMAC pair — no access to the `client_secret`, no privileged account, and no TLS interception is needed. The webhook receiving endpoint is a public HTTP endpoint by design (Shopify calls it over the internet), so replaying a captured request with modified headers is trivial for any unprivileged internet user who has legitimate access to at least one shop using the app.

### Recommendation
Bind the tenant-identifying fields to the HMAC-signed material, e.g. include `shop`, `topic`, and `webhook_id` in the string that is HMAC-verified (matching what Shopify actually signs, or by having the app framework independently correlate the header-supplied shop against a value derived from an authenticated source), rather than trusting `request.shop`/`request.topic` purely from headers once only the body HMAC has been checked.

### Proof of Concept
1. Install the app normally on `attacker-shop.myshopify.com`; trigger any event (e.g., `orders/create`) so Shopify sends a real webhook to the app's endpoint with headers `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`.
2. Capture the raw request body and the `X-Shopify-Hmac-Sha256` value.
3. Replay the identical body and HMAC header to the same endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which succeeds because it only re-derives `HMAC(body)` and compares it to the supplied signature — both unchanged from step 1: [5](#0-4) 
5. The handler executes with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` reporting `victim-shop.myshopify.com` as the source shop, even though the payload was generated for and originally signed for `attacker-shop.myshopify.com`.

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
