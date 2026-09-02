### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw body, while the `shop` (tenant identity) is read from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to attribute the webhook payload to a tenant, without any binding between the signed bytes and the shop identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` is derived purely from the `shop-domain` header, which is never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `to_signable_string` (i.e., body) against the app's `api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC, then immediately builds `WebhookMetadata` using `request.shop` — the unauthenticated header value — to tell the handler which tenant the payload belongs to: [4](#0-3) 

The identity binding the gem should enforce is:
`hmac_valid(raw_body, api_secret_key) == true` **AND** `shop == the tenant that produced raw_body`

But the gem only proves the first half. Because a Shopify app's `api_secret_key`/`client_secret` is shared across every shop that installs the app (not per-tenant), any merchant who installs the app receives genuinely-signed webhooks for their *own* shop. That merchant can then replay the exact same signed body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` dispatches the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant confusion vulnerability: a malicious or compromised installer of a multi-tenant app can cause the host application to process attacker-controlled webhook data (order data, product data, etc., depending on topic) as if it originated from any other shop that has installed the same app, since `shop` is asserted via an unauthenticated header rather than being cryptographically bound to the payload. Any host-app logic that keys tenant-scoped side effects (e.g., data writes, session lookups, notifications) off `WebhookMetadata#shop` can be manipulated to act on/attribute data to a shop the attacker does not control, satisfying the Critical "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is limited to unprivileged users who can install the target app on at least one shop (a normal, unprivileged action for any Shopify merchant), then intercept one legitimately delivered webhook for their own shop and replay it with a modified shop header to the app's public webhook endpoint. No access to the app's `client_secret`, session tokens, or other shops' credentials is required — only the ability to receive one webhook for a shop the attacker legitimately owns.

### Recommendation
Bind the shop identity into the signed payload verification path, e.g., have `Registry.process` (or `Request`) cross-check `request.shop` against a known/registered shop for the current install (via session lookup) before dispatching the handler, or require the host application to perform that check and document it as mandatory. At minimum, the gem should not present `request.shop` as a trusted value without stating this caveat, since it is not covered by `to_signable_string`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Shopify delivers a legitimate webhook, e.g. `orders/create`, to the app's registered endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and re-sends it to the same webhook endpoint, keeping body `B` and `X-Shopify-Hmac-Sha256: H` unchanged, but replacing the header with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` — validation succeeds ( [5](#0-4) ).
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` ( [6](#0-5) ), causing the host app to process attacker-controlled data as belonging to `victim-shop.myshopify.com`.

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
