### Title
Webhook `shop` identity is trusted despite not being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. The `shop` value therefore has no cryptographic binding to the signature that "proves" the request is genuine, yet `Webhooks::Registry.process` forwards this unverified `shop` value straight into `WebhookMetadata` and the app's handler as the trusted tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes and compares the HMAC exclusively over that signable string (i.e., the body): [2](#0-1) 

Meanwhile, `Request#shop` is read straight from a header that is never mixed into the signed content: [3](#0-2) 

`Registry.process` validates the HMAC once, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) to build `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because only the body is authenticated, the binding "shop claimed in the header" == "shop that actually produced/authorized this signed payload" does not hold. An unprivileged attacker who owns any Shopify store (trivial and free to create — dev/partner sandbox stores) can:
1. Install the target app on their own attacker-controlled shop and receive a legitimately HMAC-signed webhook (valid signature over a body of the attacker's choosing/controllable topic).
2. Replay that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is valid), and `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, handing the attacker-controlled body to the app's handler under the victim's tenant identity.

Any app logic that keys off `data.shop` (as the gem's own docs instruct — `shop`, `String` - "The shop domain of the webhook") to select a session, write to a per-shop database record, or otherwise act as that tenant will now act on behalf of the victim shop using attacker-supplied data.

### Impact Explanation
This breaks tenant isolation: the `shop` identity is acted upon by downstream app code without being cryptographically bound to the HMAC that supposedly authenticates the whole webhook request. This is a cross-tenant access primitive — an attacker with no access to the victim's credentials or access tokens can inject data/events attributed to an arbitrary victim shop merely by forging the `shop-domain` header on an otherwise-valid (self-obtained) signed payload.

### Likelihood Explanation
High. Creating a legitimate Shopify development/partner store and installing the target app is free and requires no privileged access. Forging or replaying with a modified header is trivial for anyone who can send arbitrary HTTP requests to the app's public webhook endpoint. No secret key, access token, or victim credential is required.

### Recommendation
Do not treat `Request#shop` (or `topic`/`webhook_id`/`api_version`) as authenticated unless they are part of the signed content. Either:
- Include the shop domain (and other identity-relevant headers) in the string that is HMAC-verified, matching them against the body's canonicalized representation, or
- At minimum, document/require that host applications cross-check `data.shop` against an already-known/registered shop list (not just accept it because the request "passed HMAC"), and ensure `Registry.process` doesn't imply header integrity guarantees it doesn't actually provide.

### Proof of Concept
1. Attacker creates a free Shopify dev store `attacker-shop.myshopify.com` and installs the target app.
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (valid signature of `B` under the app's `api_secret_key`, since HMAC is only computed over `B`).
3. Attacker sends a new POST to the same app webhook endpoint with:
   - Body: `B` (unchanged, so `H` still validates)
   - Header `x-shopify-hmac-sha256: H`
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic`: unchanged/attacker-chosen
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because `to_signable_string` only checks `B`/`H`.
5. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and invokes the app handler, which now processes attacker-controlled data as if it came from the victim shop.

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
