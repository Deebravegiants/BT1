The docs explicitly state that `Registry.process` "will verify the request did indeed come from Shopify" — this is the library's own documented guarantee, and the library implements that guarantee solely via `Utils::HmacValidator.validate(request)`, whose signable string is only the raw body:

```ruby
# lib/shopify_api/webhooks/request.rb
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
def shop
  T.cast(shopify_header("shop-domain"), String)
end
def to_signable_string
  @raw_body
end
```

`request.shop` is read straight from the `X-Shopify-Shop-Domain` header, which is never part of `to_signable_string` and therefore is completely outside the HMAC binding. `Registry.process` then forwards this unauthenticated `shop` value directly to the app's handler as the tenant identity:

```ruby
# lib/shopify_api/webhooks/registry.rb
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

### Title
Webhook tenant identity (`shop`) is not bound to the HMAC-verified payload, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify," but the only integrity check performed, `Utils::HmacValidator.validate(request)`, signs solely the raw request body. The `shop` value that is delivered to the application's webhook handler as the trusted tenant identifier is read from the `X-Shopify-Shop-Domain` header, which is never included in the HMAC-signed material, breaking the binding `shop_authenticated == shop_used_as_tenant_key`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate_signature` computes/compares the HMAC purely over that signable string [2](#0-1) . Meanwhile `Webhooks::Request#shop` is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , which is disjoint from the signed bytes. `Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity passed to the handler without any cross-check that ties the verified body to that specific shop [4](#0-3) . Since an app's webhook signing secret (`client_secret`) is shared across every shop that installs the app, any account holder (even an attacker who legitimately installs the same public app on their own store) can capture a fully valid, HMAC-signed webhook triggered by their own store's events, then replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop. The `hmac` check still passes (it only covers the untouched body), and `Registry.process` hands the handler a `WebhookMetadata` claiming the event belongs to the victim shop. The library's own documentation for `process` explicitly promises the request is verified as coming from Shopify, giving developers no signal that they must independently re-verify the shop domain against an installed-shop list themselves.

### Impact Explanation
This breaks the tenant boundary the library is meant to enforce for webhook processing: an attacker with no privileges over the victim's store can cause an app to process attacker-controlled data under the victim shop's identity (`data.shop`), potentially triggering shop-scoped business logic (e.g., data sync, order/customer records keyed by `shop`, entitlement changes) attributed to the wrong tenant — a cross-tenant integrity violation.

### Likelihood Explanation
Any user can install a public app that uses this gem on their own development/trial store at no cost, generate genuine webhook traffic for that store (a valid HMAC signed with the shared `client_secret`), capture the raw request, and replay it against the app's public webhook endpoint with only the shop-domain header modified — no secrets, tokens, or credentials belonging to the victim are required.

### Recommendation
Bind the tenant identity into the checked material: either include the shop domain (and topic/webhook-id) in the value that is HMAC-verified, or require callers of `Registry.process`/`WebhookMetadata` to supply and check the `shop` against the app's own list of shops that have valid sessions/registrations, rejecting webhooks for shops the app does not recognize before invoking the handler. At minimum, update the documentation and `WebhookMetadata` contract to explicitly state that `shop` is unauthenticated and must be independently verified by the application before use.

### Proof of Concept
1. Install the vulnerable app (built on this gem) on attacker-controlled store `attacker.myshopify.com`.
2. Trigger a webhook event (e.g., `orders/create`) on the attacker's own store; capture the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify (valid, since signed with the app's shared `client_secret`).
3. Replay the exact same raw body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the untouched raw body [5](#0-4) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` [6](#0-5) , causing the application to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
