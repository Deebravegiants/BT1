## Title
Webhook HMAC Does Not Bind the `shop`/`topic` Identity Headers — Allows Cross‑Tenant Webhook Forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC verification performed by `HmacValidator` authenticates the JSON payload bytes but never binds the `X-Shopify-Shop-Domain` (or `X-Shopify-Topic`) header to that signature. `Registry.process` nevertheless trusts the unauthenticated `shop` header as the tenant identity handed to the app's webhook handler. This is the same bug class as the reported `hashAssignment()` issue: a field that materially determines downstream execution (`metaHash` there, the shop/tenant identity here) is not covered by the cryptographic commitment, so an unprivileged holder of *any* validly-signed body can retarget it.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

It returns only `@raw_body`. `HmacValidator.validate` computes the HMAC exclusively over this signable string: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which participate in the signature: [3](#0-2) 

`Registry.process` validates the HMAC and then passes the **unauthenticated** `request.shop` value directly into the tenant-identifying metadata delivered to the host application's handler: [4](#0-3) 

The identity binding that should hold is:
```
shop authenticated by HMAC == shop used to route/process the webhook
```
Because only `@raw_body` is hashed, this equality does not hold: `shop cryptographically bound = ∅`, while `shop used for tenant routing = request.shop` (an attacker-controlled header).

### Impact Explanation
Any user who can obtain one validly-signed `(raw_body, hmac)` pair from Shopify — trivially achievable by installing the target app on a shop they control (even a free development store) and triggering any webhook event — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`) with a victim shop's domain. `Registry.process` will accept the HMAC as valid (it only checks the body bytes) and dispatch the payload to the handler tagged with the attacker-chosen `shop`, i.e., cross-tenant data being attributed to/processed for the wrong merchant. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., to look up the merchant's session/access token, update records, or trigger tenant-scoped side effects), this enables cross-tenant access/data corruption without the attacker ever needing the app's `client_secret` or a victim's access token — meeting the "cross-tenant access" Critical impact bar.

### Likelihood Explanation
High for any host application that trusts `WebhookMetadata#shop` for authorization/routing after `Registry.process` succeeds (this is the intended usage pattern documented for this gem). The only prerequisite is the ability to capture one legitimately-signed webhook, which is available to anyone able to install the app on any shop, including their own.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them (e.g., via a MAC over `shop || topic || raw_body`). Until fixed, host applications should independently verify that the shop in the webhook matches an installed/authorized shop before acting on the payload — but the gem's own `hashAssignment`-style contract (payload verified ⇒ headers trustworthy) is currently broken.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g., `orders/create`). Capture `raw_body` and the resulting `X-Shopify-Hmac-Sha256` value — both are legitimately produced by Shopify using the app's real `client_secret`.
2. POST this exact `raw_body` to the app's webhook endpoint, but set:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create` (unchanged or altered, also unauthenticated)
   - `X-Shopify-Hmac-Sha256: <the captured signature>` (unchanged, since body is unchanged)
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only hashes `raw_body`: [1](#0-0) 
4. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`: [5](#0-4) 
   The host application processes attacker-supplied data under the victim shop's identity.

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
