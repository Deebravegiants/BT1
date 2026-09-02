## Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` binds the shop identity used for webhook routing to the raw `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` validates is computed only over the raw request body. The `shop` value that host applications use to attribute the event to a tenant is therefore never authenticated, breaking the equality that should hold: `shop_verified_by_hmac == shop_used_for_tenant_routing`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from an unauthenticated header with no cryptographic tie to the body or the signature: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature strictly from `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it never mixes in the `shop` header: [3](#0-2) 

`Registry.process` uses this validation result as the sole authenticity gate, then forwards the attacker-controlled `request.shop` straight to the handler as the tenant identifier: [4](#0-3) 

Because the api_secret_key is shared across every merchant of a given app (it is not per-shop), any legitimately-obtained `(raw_body, hmac)` pair — for example one an attacker receives for their own store after installing the app — remains valid for *any* `shop-domain` value the attacker chooses to send with it. The HMAC only proves "this body was signed once by our app secret"; it proves nothing about which shop the event belongs to. This is exactly the batchId-style identity-binding gap from the reference report: a field that is acted upon (`shop`, used for tenant routing) is not covered by the authentication check (`hmac`, computed over `raw_body` only).

### Impact Explanation
A host application built on this gem typically uses `WebhookMetadata#shop` (populated from `request.shop`) to decide which merchant's data store to update, e.g. `Order.where(shop: data.shop).update(...)`. Since `shop` is unauthenticated, an attacker who has captured or legitimately received one valid signed webhook body (e.g., from their own free/dev store installation of the target app) can replay that exact body/HMAC pair while substituting an arbitrary victim `shop-domain` header. `Registry.process` will accept it as valid and hand the handler data purportedly belonging to the victim shop, resulting in cross-tenant data corruption/injection — data intended for the attacker's own shop is attributed to another merchant's tenant, or vice versa. This matches the Critical "cross-tenant access" bucket.

### Likelihood Explanation
Exploitation requires no credentials, no access token, and no privileged account — only network access to the app's public webhook endpoint and a single legitimately-received webhook body/HMAC pair (trivially obtainable by installing the target app on any store, including a free development store the attacker controls). The `shop` header can be freely set on the replayed HTTP request since nothing in `Request` or `Registry` binds it to the signature.

### Recommendation
Include the shop domain (and ideally the webhook id/topic) in the signed material that `HmacValidator` checks, or require the caller to independently verify that `request.shop` matches an actual known/installed shop before trusting it, rather than relying solely on `Utils::HmacValidator.validate(request)` (body-only) as the authenticity boundary. At minimum, document prominently that `Request#shop` is not covered by the HMAC and must not be trusted as an authenticated tenant identifier without additional binding to the currently signed payload.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com"})` builds successfully (`shop` header present is all that's checked, per `lib/shopify_api/webhooks/request.rb` lines 50-59).
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)` which recomputes `HMAC(secret, B)` and matches `H` — validation **passes** (`lib/shopify_api/utils/hmac_validator.rb` lines 26-31), because the shop header was never part of the signed input.
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb` lines 198-199), causing the host app to process attacker-supplied data under the victim shop's tenant context.

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
