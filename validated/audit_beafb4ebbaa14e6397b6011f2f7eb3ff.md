### Title
Webhook shop-domain (and topic/webhook-id) identity spoofing via HMAC that only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC solely against that body, so a valid HMAC never proves which shop, topic, or webhook the payload belongs to. An attacker who legitimately installs the target app on their own store (an ordinary, unprivileged action) receives real webhooks with a body and HMAC signed by the app's real `client_secret`. They can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop, and the request still passes `HmacValidator.validate` unchanged.

### Finding Description
`to_signable_string` in `lib/shopify_api/webhooks/request.rb` is defined as:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

but the fields consumed by the handler are pulled straight from headers with no cryptographic tie to the body:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`HmacValidator.validate_signature` computes the signature only from `to_signable_string` and compares it against the received `hmac`, never incorporating `shop`, `topic`, or `webhook_id`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [3](#0-2) 

`Registry.process` then trusts the header-derived `shop`/`topic`/`webhook_id` immediately after this single body-only check:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

The binding the gem is expected to guarantee is:
`hmac_valid(body, secret) == true  ⇒  shop_header == the shop Shopify actually generated this payload for`

Because `shop-domain` (and `topic`/`webhook_id`) are outside the signed bytes, this equality does not hold — any header combination accompanying an already-valid `(body, hmac)` pair passes verification, regardless of which shop it is attributed to.

### Impact Explanation
An unprivileged internet user who installs the target app on their own Shopify store obtains legitimately signed `(raw_body, hmac)` pairs (correctly signed with the app's real `client_secret` by Shopify itself — no secret leakage or credential theft is required). By resending that identical body/HMAC to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop, the request still passes `HmacValidator.validate`, and the app's `WebhookMetadata` is built using the attacker-chosen `shop` value. Any app logic that keys off `WebhookMetadata#shop` to select which tenant's session/record to update (a documented and expected usage pattern for this gem) will process/act on data attributed to a different shop than what Shopify actually signed for — a cross-tenant identity binding break.

### Likelihood Explanation
Moderate-to-high: no secret, TLS interception, or privileged access is needed — only the ability to install the app on one's own store (a normal, self-service action) and to send a crafted POST request to the app's public webhook endpoint, both are within reach of an unprivileged internet user.

### Recommendation
Bind the shop/topic/webhook identity to the signed content:
- Reject webhooks unless the caller independently confirms `shop` against a known, previously-established relationship (e.g., an existing session for that shop) before acting, rather than trusting the header value alone once HMAC passes.
- Where feasible, incorporate `shop`, `topic`, and `webhook_id` into the value that is HMAC-verified (or provide an explicit, documented API contract requiring host apps to cross-check `shop` against their own session store before processing), so a valid HMAC cannot be replayed across shop identities.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker-shop.myshopify.com`) and triggers a webhook (e.g., updates a product), receiving from Shopify a POST to the app's public webhook URL with:
   - body: `raw_body`
   - `x-shopify-hmac-sha256`: valid HMAC of `raw_body` using the app's real `client_secret`
   - `x-shopify-shop-domain`: `attacker-shop.myshopify.com`
2. Attacker captures this exact `(raw_body, hmac)` pair (their own server/webhook logs — no interception of anyone else's traffic needed).
3. Attacker sends a new POST directly to the same app's public webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over `raw_body` only, matches it against the unchanged `hmac`, and returns `true`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches it to the app's handler, which now believes the payload originated from the victim shop.

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
