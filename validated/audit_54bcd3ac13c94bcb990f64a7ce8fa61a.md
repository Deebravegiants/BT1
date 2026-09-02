### Title
Webhook `shop-domain` header is trusted as tenant identity but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC only over the raw HTTP body, while the `shop` (tenant identity) that is handed to the application's webhook handler is read from an unauthenticated header. The binding the gem is supposed to enforce — `HMAC-verified bytes == identity bytes acted upon` — does not hold, because the `shop-domain` header is not part of the signed data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `HmacValidator.validate` verifies the HMAC exclusively against that signable string: [2](#0-1) 

`Registry.process` uses `Utils::HmacValidator.validate(request)` as the sole authenticity check for an inbound webhook, then immediately trusts `request.shop` (parsed straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, never included in the HMAC computation) to build the `WebhookMetadata` passed to the application's handler: [3](#0-2) [4](#0-3) 

Because the `shop` header is never mixed into `to_signable_string`, the equality the gem should be enforcing —`hmac(body) with binding to shop == hmac(body) as verified` — is broken: the HMAC only proves "this body was sent by someone possessing `api_secret_key`", not "this body belongs to this shop." Any `(body, hmac)` pair produced for one tenant (e.g., an attacker's own development/trial store, for which they legitimately receive real, validly-signed webhooks from Shopify) remains valid when replayed with an arbitrary `shopify-shop-domain` header value, since that header plays no role in `validate_signature`.

### Impact Explanation
An unprivileged internet user who operates their own Shopify store (a routine, free action) receives genuine webhook deliveries for that store, each with a valid HMAC over the body. Because the header carrying the shop identity is unauthenticated, that same `(body, HMAC)` pair can be resent to the merchant application's public webhook endpoint with the `shopify-shop-domain` header rewritten to name a victim shop. `HmacValidator.validate` still passes (it only checks the body/secret), and `Registry.process` dispatches to the registered handler with `WebhookMetadata#shop` set to the victim's shop domain while the `body` content is the attacker's own. Any host application that follows this gem's documented contract — trusting `data.shop` from a successfully-processed webhook to select the tenant record to update — will apply attacker-controlled data under a victim tenant's identity, i.e. cross-tenant data injection/confusion, satisfying the "cross-tenant access" Critical impact class.

### Likelihood Explanation
The prerequisite (owning any Shopify store to harvest a legitimately-signed webhook body/HMAC pair) is trivially available to any unprivileged internet user, and mandatory webhook topics such as `customers/redact` / `customers/data_request` / `shop/redact` produce small, predictable bodies that are easy to replay across many different forged `shop-domain` values. No access token, `api_secret_key`, or privileged access is required.

### Recommendation
Bind the identity fields that the application will act on (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) into the signed material verified by `HmacValidator`, e.g. by having `Request#to_signable_string` incorporate the shop-domain header alongside the raw body, or by independently verifying that the shop present in the header matches an out-of-band expectation before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` (or any store they control) and lets Shopify deliver a normal webhook, e.g. `customers/data_request`, capturing the raw body `B` and header `x-shopify-hmac-sha256: H` (`H = HMAC-SHA256(secret, B)`, unknown secret, but valid pair).
2. Attacker sends a POST to the merchant app's webhook endpoint with:
   - body = `B`
   - `x-shopify-hmac-sha256: H` (unchanged, still valid because HMAC only covers body)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic: customers/data_request`
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `B` against `H`, per `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, per `lib/shopify_api/webhooks/registry.rb:198-199`, even though the body/HMAC pair was never associated with `victim-shop.myshopify.com` by Shopify.

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
