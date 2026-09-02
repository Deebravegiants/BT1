### Title
Webhook `topic` and `shop-domain` Headers Are Trusted Without Being Covered by the HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only. The `topic` and `shop-domain` values used by `Registry.process` to dispatch and attribute the webhook to a tenant are read from separate, unsigned HTTP headers, so any request with a validly-signed body can be replayed with an arbitrary `shop`/`topic` pair and will still pass `HmacValidator.validate`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic`, however, are read straight from attacker-controllable HTTP headers and are never mixed into the signed string: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC solely against `to_signable_string`, i.e. the body bytes: [3](#0-2) 

`Registry.process` accepts the request once `HmacValidator.validate(request)` is true, then dispatches to the handler using the unauthenticated `request.shop` and `request.topic` values, packaged into `WebhookMetadata` that the host application relies on to attribute the event to a tenant: [4](#0-3) [5](#0-4) 

The binding the gem should enforce is: `hmac == HMAC(secret, body || shop || topic)` (or at minimum, that the verified bytes include the fields the caller trusts). Instead the code enforces `hmac == HMAC(secret, body)` while consumers trust `shop`/`topic` as if they were verified. Because Shopify's per-app webhook signing secret (`api_secret_key`) is the same for every shop that installs the app, any unprivileged user can install the target app on their own shop, receive genuine, validly-HMAC'd webhook deliveries for that shop, and then replay the exact same signed body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks the untouched body bytes, and `Registry.process` forwards `WebhookMetadata(shop: <attacker-chosen>, topic: <attacker-chosen>, ...)` to the host app's handler as if Shopify itself vouched for that shop/topic pairing.

### Impact Explanation
This breaks the tenant-identity binding the gem is supposed to provide (`shop` field acted on by `Registry.process`/`WebhookHandler#handle` but not covered by the HMAC). A host application that keys its per-tenant data, session lookups, uninstall/redact logic, or billing state off `WebhookMetadata#shop` can be made to apply mutations intended for the attacker's shop to a completely different, victim shop (e.g., forging `app/uninstalled` or `shop/redact` for a victim shop, or injecting fabricated `orders/create`/`customers/data_request` events attributed to a shop the attacker never controls). This is a cross-tenant integrity violation reachable by any unprivileged actor who can install the app on their own store — no access token, `client_secret`, or privileged account is required.

### Likelihood Explanation
High likelihood: any developer/partner can install a public app on a free/dev store, trigger a real webhook delivery for any subscribed topic, capture the raw body + valid HMAC, and replay it with modified `shop-domain`/`topic` headers to the same webhook endpoint. No secret material or special access is needed beyond normal, self-service app installation.

### Recommendation
Include the `shop` (and ideally `topic`) values in the signed payload that `HmacValidator` verifies, or otherwise cryptographically bind them to the raw body (e.g., verify a canonicalized string of `shop-domain + topic + raw_body`) before trusting `request.shop`/`request.topic` in `Registry.process`. At minimum, document prominently that `Request#shop` and `Request#topic` are not covered by HMAC verification and must not be used as an authorization/tenant boundary without additional server-side verification (e.g., cross-checking against the shop's registered webhook endpoint URL or a session-derived shop).

### Proof of Concept
1. Attacker signs up as a Shopify partner/dev and installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a subscribed webhook topic (e.g. `customers/data_request`) on their own shop, capturing the raw POST body and the genuine `X-Shopify-Hmac-Sha256` header value sent by Shopify (computed with the app's shared `api_secret_key`).
3. Attacker replays the exact same body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `HmacValidator.validate(request)` in `Registry.process` succeeds because it only hashes `@raw_body`, which is unmodified and still matches the supplied HMAC.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, and the host application processes it as an authentic event for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
