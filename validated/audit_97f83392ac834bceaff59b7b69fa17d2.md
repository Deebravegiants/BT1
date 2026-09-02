## Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts an entirely separate, HMAC-uncovered header to determine which shop (tenant) the payload belongs to. Because the `shop` value used to dispatch tenant-scoped processing is never part of the signed material, a party that possesses one valid `(raw_body, hmac)` pair for a webhook — trivially obtainable by any merchant who has the app installed and receives webhooks at their own endpoint — can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header. The signature check still succeeds because it never covers the shop field, and the handler is invoked believing the payload originated from the spoofed shop.

### Finding Description
`Webhooks::Request` computes the authenticating HMAC purely from the raw body: [1](#0-0) [2](#0-1) 

The `shop` accessor, used to identify which tenant/session the webhook belongs to, is read from a completely separate header that is not included in `to_signable_string`: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards `request.shop` (the unauthenticated header) straight to the app's handler as the tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`shop used by HmacValidator.validate(request)` == `shop delivered to the handler as WebhookMetadata#shop`

In reality, `HmacValidator.validate` only checks `OpenSSL.secure_compare(computed_signature, received_signature)` over the raw body: [5](#0-4) 

Since `shop-domain` never enters `to_signable_string`, the two sides of the binding are disjoint: the HMAC authenticates "this body came from Shopify with our secret," but nothing authenticates "this body is destined for shop X." Any header value can be attached to a validly-signed body without breaking the signature check.

### Impact Explanation
An attacker who has installed the app on their own store (an unprivileged-internet-user relative to any other merchant's tenant) receives real webhooks with real, validly computed HMACs for their own body payloads. By replaying the exact `raw_body` + `hmac-sha256` header pair to the app's webhook endpoint while changing `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) to point at a victim shop, the attacker gets `HmacValidator.validate` to pass and `WebhookMetadata#shop` populated with the victim's domain. Any host application logic that uses `data.shop` to select which merchant's session/access token/database record to update (which is exactly the intended and documented use of this field, per `WebhookMetadata`) will operate on the victim tenant using attacker-controlled body content — a cross-tenant data injection/confusion primitive reachable purely from the network, with no access token or `client_secret` required.

### Likelihood Explanation
Likelihood is high for any host app that follows the gem's own advertised pattern of trusting `WebhookMetadata#shop`/`#body` for tenant dispatch. The only prerequisite is that the attacker have a working installation of the app on some shop (an ordinary unprivileged action any internet user can take by installing a public Shopify app), letting them capture one legitimate `(body, hmac)` pair and then send an arbitrary HTTP POST to the webhook receiver with a forged shop header.

### Recommendation
Include the shop domain (and other tenant-identifying headers such as `webhook-id`, `api-version`) inside the signed material verified by `HmacValidator`, or otherwise cryptographically bind `request.shop` to the HMAC-covered payload before it is handed to `WebhookMetadata`. At minimum, document and enforce that host applications must independently corroborate the `shop-domain` header against a value derived from authenticated content (e.g., a `shop`/`admin_graphql_api_id` embedded in the JSON body) rather than trusting the header alone.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook at the app's endpoint:
   - Headers: `x-shopify-hmac-sha256: <valid-hmac-for-body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`
   - Body: `{"id": 1, ...}` (attacker fully controls the resource content on their own store, e.g. by placing an order with self-chosen data)
2. Attacker captures the raw body bytes and the corresponding `x-shopify-hmac-sha256` value exactly as sent by Shopify.
3. Attacker resends the identical body and HMAC to the app's webhook endpoint, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` only (`Webhooks::Request#to_signable_string`) and it matches, so validation succeeds despite the shop header being forged.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the host application to process attacker-supplied data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
