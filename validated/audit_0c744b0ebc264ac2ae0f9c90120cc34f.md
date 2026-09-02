### Title
Webhook `shop` (and `topic`) identity is trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface, but its `to_signable_string` returns only the raw HTTP body — it never binds the `shopify-shop-domain` (or `shopify-topic`) header into the signed content. `Utils::HmacValidator.validate` therefore only proves that Shopify signed *this body*, never that Shopify sent it *for this shop* or *for this topic*. Because the shop identity used for tenant routing is not part of the HMAC-covered bytes, an attacker who can obtain one legitimately-signed webhook (from their own shop where the app is installed) can replay the same body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header, and the gem will accept it as valid and hand the forged shop identity to the host application's webhook handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
only the `@raw_body` is included. The `shop` accessor, however, is read straight from an unauthenticated header: [2](#0-1) 
and the same is true of `topic`: [3](#0-2) 

`Registry.process` validates only the HMAC of the body and then unconditionally trusts `request.shop` and `request.topic` to build the metadata delivered to the app's handler: [4](#0-3) 

The equality that should hold is:
`shop bound by HMAC == shop used for tenant routing`

but the actual behavior is:
`shop bound by HMAC (none — HMAC covers body only) != shop used for tenant routing (attacker-controlled header)`

Because `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) recomputes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header, it never observes or constrains the `shop-domain`/`topic` headers. This is structurally the same class of bug described in the external report: the verification mechanism ("check the sequence"/"check the signature") is reused to cover fields it was never designed to bind, letting an attacker satisfy the check while still controlling an out-of-band field that downstream logic depends on for correctness.

### Impact Explanation
An unprivileged internet user who can install (or already has) the app on their *own* shop can receive a legitimately Shopify-signed webhook for that shop (any topic they can trigger, e.g. `orders/create`, `customers/data_request`, etc.). They can replay that exact body + `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint while setting `X-Shopify-Shop-Domain` to a victim shop's domain. `Registry.process` will pass HMAC validation and invoke the host app's handler with `WebhookMetadata#shop` set to the victim's domain and attacker-controlled body content — this is a cross-tenant data-integrity violation: the app processes attacker-supplied data attributed to another merchant's tenant, satisfying the Critical "cross-tenant access" category. It can also be combined with topic substitution to route one shop's payload into a handler intended for a different topic, causing incorrect business-logic execution (e.g. false `app/uninstalled` or `orders/create` processing) for a targeted shop.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app on any shop (many Shopify apps are public/installable by any developer or merchant), and (2) the ability to trigger at least one webhook delivery from that shop. Both are available to an ordinary, unprivileged Shopify user with no access to the app's `client_secret`, access tokens, or any victim credentials — only knowledge of the app's public webhook endpoint. The replay is a simple HTTP request with a modified header.

### Recommendation
Include the shop domain (and ideally the topic) in the HMAC-verified surface, or otherwise cryptographically bind them — e.g., require the host application to independently verify `request.shop` against a known/installed-shop registry before trusting it, and/or extend `to_signable_string` (or add a separate binding check in `Registry.process`) so the signature covers `shop-domain`/`topic` in addition to the body. At minimum, document clearly that consumers of `WebhookMetadata#shop` and `#topic` must not treat them as authenticated unless independently cross-checked against session/tenant state, since today `Utils::HmacValidator` only proves body integrity, not sender identity for those fields.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and its valid `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's real `client_secret`).
2. Attacker sends a new POST to the app's webhook endpoint with:
   - Body: the same `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic: orders/create` (unchanged or changed to another topic the attacker wants to trigger)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only [5](#0-4)  — validation succeeds because `B` and `H` still match.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [6](#0-5) , causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-18)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
