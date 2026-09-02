### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop` (tenant) identity used by the webhook handler comes from the `X-Shopify-Shop-Domain` header, which is never included in the signed material. `HmacValidator.validate` only proves the body bytes are intact/authentic; it says nothing about which shop the body belongs to. This breaks the intended identity binding: `shop_verified_by_hmac == shop_used_by_handler`.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it against the received signature using the app's `api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely outside the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches to the handler using `request.shop`, trusting it as the authenticated tenant identity: [4](#0-3) 

Because the same `api_secret_key` is shared across every shop that has installed a given app, any unprivileged user who legitimately installs the app on their own store can trigger a real, validly-HMAC-signed webhook body (e.g. by creating an order that they fully control the content of). They can then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still passes (the body/HMAC pair is untouched and valid), and `Registry.process` forwards `WebhookMetadata` tagged with the attacker-chosen `shop` value to the app's handler: [5](#0-4) 

The equality that should hold — the shop cryptographically bound to the signed bytes equals the shop the application acts on — does not hold: the HMAC binds nothing about tenant identity, only body integrity.

### Impact Explanation
This enables cross-tenant data injection: a host application that (reasonably, given this gem's API) trusts `WebhookMetadata#shop` once `HmacValidator.validate` succeeds will process attacker-supplied webhook content (order/customer/product payloads it fully controls from its own store) as if it belonged to a victim tenant. This is a cross-tenant access/data-integrity violation reachable by any unprivileged user who can install the app on any shop (including their own), without needing the victim's or the app's secrets.

### Likelihood Explanation
Likelihood is moderate to high in multi-tenant apps that key business logic (order sync, billing, entitlement, provisioning) off of `WebhookMetadata#shop` under the assumption that a validated HMAC implies a validated shop. No credentials beyond a normal, unprivileged app install are required; the attacker fully controls the webhook body content sent from their own store and simply forges the shop header on replay.

### Recommendation
Bind the shop domain into the value that is cryptographically checked, or require the caller to cross-check `request.shop` against a shop for which the app already holds a valid, previously issued session/access token before trusting the webhook payload as belonging to that shop. At minimum, document prominently that `HmacValidator.validate` on webhooks authenticates the body only, not the `shop` header, and that consumers must independently verify tenant identity (e.g., against known installed shops) before acting on webhook data.

### Proof of Concept
1. Install the target app on an attacker-controlled store `attacker.myshopify.com` (a normal, unprivileged action).
2. Trigger a webhook subscribed by the app (e.g. `orders/create`) with a body the attacker fully controls (order line items, customer info, etc.). Capture the resulting `raw_body` and the genuine `X-Shopify-Hmac-Sha256` value — both are valid because Shopify signs with the same `api_secret_key` used for every shop of this app.
3. Replay the identical `raw_body`/`X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are computed purely from `raw_body`/the hmac header, so `HmacValidator.validate` returns `true` [6](#0-5) .
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic:, shop: request.shop, body: request.parsed_body, ...)` where `shop` is `"victim-shop.myshopify.com"` [7](#0-6) , causing the host app to process attacker-crafted data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
