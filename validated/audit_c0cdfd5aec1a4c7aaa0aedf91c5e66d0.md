Based on my investigation, I found a concrete instance of the identity-binding break described in the rules.

### Title
Webhook `shop` identity is taken from an unauthenticated header not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, but exposes a `shop` accessor that is read directly from the `X-Shopify-Shop-Domain` HTTP header. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` as the tenant identity handed to the app's webhook handler, even though that header was never part of what the HMAC signed.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC solely against that signable string [2](#0-1) . Meanwhile, `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the HMAC-covered bytes [3](#0-2) .

`Registry.process` verifies only the HMAC (over the body) and then immediately builds `WebhookMetadata` using `request.shop` as the trusted tenant identifier passed to the app's handler: [4](#0-3) .

The binding that should hold is: `shop attributed to this delivery == shop cryptographically bound inside the HMAC-covered bytes`. In this implementation that equality does not hold — `shop` is parsed from headers that are outside the HMAC-signable string, while only the JSON body bytes are verified.

Concretely: if any component in front of this gem (a proxy, a shared endpoint, a bug in body/header pairing, or a Shopify-side inconsistency) allows the `X-Shopify-Shop-Domain` header value to diverge from the shop whose secret actually produced the HMAC over the body, this gem will still accept the request as valid (since HMAC validation never looks at the shop header) and will report the attacker/other-tenant's shop string to the handler as the authenticated tenant.

### Impact Explanation
If the shop attribution given to the app's webhook handler can be desynchronized from the HMAC-covered payload, this creates a cross-tenant data misattribution path: the handler could process/store webhook data under the wrong shop's record, mixing tenant data or letting one merchant's webhook be attributed to another merchant's account (`WebhookMetadata#shop`). This falls in the "cross-tenant access" impact category.

### Likelihood Explanation
This is a design property of the gem itself (not a host-app misuse): every consumer of this library that follows the documented `Registry.process` flow inherits the same trust boundary — the HMAC only proves the body was signed by *some* holder of the API secret, it does not prove which header-supplied shop that signature belongs to. The likelihood of exploitation depends on whether an attacker can control or manipulate the `X-Shopify-Shop-Domain` header independently of the signed body in a given deployment (e.g., behind a shared endpoint accepting webhooks for multiple apps/shops, or any transport that lets headers and body diverge), which is plausible but not guaranteed in a single-app-single-endpoint deployment.

### Recommendation
Include the shop domain (and other webhook metadata Shopify guarantees, like `topic`) inside the HMAC-covered signable string, or independently verify that the `shop` header value matches a shop known/expected by the app (e.g., cross-check against stored sessions) before trusting it in `WebhookMetadata`. At minimum, document that `request.shop` is not authenticated by the HMAC and must not be used as a sole tenant-identity source in security-sensitive handler logic.

### Proof of Concept
1. Attacker obtains a legitimately signed webhook payload for `shop=victim-a.myshopify.com` (e.g., via a shared/multi-tenant relay, or replays an HMAC computed for the same body under the app's single shared `client_secret` used across all its installs).
2. Attacker sends this raw body unchanged (preserving valid HMAC) but with `X-Shopify-Shop-Domain: victim-b.myshopify.com` to the app's webhook endpoint.
3. `Utils::HmacValidator.validate` at [5](#0-4)  succeeds because it only checks the body bytes against the shared secret.
4. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` == `"victim-b.myshopify.com"` [6](#0-5) , and the app's handler now processes victim-a's webhook payload under victim-b's tenant context.

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
