### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant) identity used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and label the webhook is read from an unsigned HTTP header. This breaks the equality `shop authenticated by HMAC == shop used as the webhook's tenant identity`, allowing a party who can obtain one valid `(raw_body, hmac)` pair for their own shop to replay it against the app's webhook endpoint while claiming to be a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` (which only checks `to_signable_string`, i.e. the body) and then immediately trusts `request.shop` as the tenant identity passed to the handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` only ever compares `verifiable_query.hmac` against a signature computed from `verifiable_query.to_signable_string`; for webhook requests that string never includes the shop domain: [4](#0-3) 

Because the app's `client_secret` (`Context.api_secret_key`) is a single static per-app secret (not per-shop), the HMAC only proves "this body was signed by someone possessing the app secret" — it does not prove which shop the body belongs to. Any actor who can trigger one legitimate webhook for a shop they control (e.g., by installing the app on their own store and generating an event) can capture a valid `(raw_body, hmac)` pair, then send an HTTP request to the app's webhook endpoint with the same body/HMAC but an attacker-chosen `shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` still succeeds (it never inspects the header), and `Registry.process` forwards `WebhookMetadata.new(topic:, shop: request.shop, body: request.parsed_body, ...)` to the app's handler labeled with the victim's shop identity.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem lets a caller who can only prove possession of one legitimate signed payload attribute that payload's data/processing to an arbitrary other merchant. Any app logic keyed off `WebhookMetadata#shop` (session lookup, per-tenant data writes, mandatory GDPR `shop/redact`/`customers/redact`/`customers/data_request` handling, billing/webhook-driven state transitions) can be triggered or polluted for a shop the attacker does not own, which is a cross-tenant access impact.

### Likelihood Explanation
Requires only the ability to install the app (or otherwise trigger one webhook) on an attacker-controlled shop plus the ability to send an HTTP request with custom headers to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed. This is realistically reachable by any unprivileged internet user for public apps that accept installs.

### Recommendation
Include the shop domain (and ideally topic) as part of the HMAC-signed material for webhook requests, or otherwise cryptographically bind the `shop` header value to the signature verification step in `HmacValidator`/`Registry.process`, rejecting requests where the asserted shop is not covered by the HMAC.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any registered webhook topic to receive one legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair from Shopify.
2. Replay an HTTP POST to the app's webhook endpoint using the same `raw_body` and `hmac` header, but set `X-Shopify-Shop-Domain: victim.myshopify.com` and the desired `X-Shopify-Topic`.
3. `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb#L190`) succeeds because it only checks the body against the app secret.
4. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload originated from the attacker's own shop, demonstrating cross-tenant identity confusion.

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
