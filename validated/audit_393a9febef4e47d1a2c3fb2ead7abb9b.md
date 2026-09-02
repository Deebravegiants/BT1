### Title
Webhook `shop` identity not covered by HMAC signature allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop identity used to route and label the delivered webhook (`shop-domain` header) is never included in the signed material. An attacker who owns a legitimate installation of the app on their own store can capture a validly-signed webhook and re-send it to the app's callback endpoint with a modified `shop-domain` header, causing the gem to report the payload as coming from a victim shop while the HMAC check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor is read straight from an unauthenticated HTTP header and is never part of the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` against the computed HMAC — for a webhook `Request`, that is exclusively `@raw_body`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the authoritative tenant identity when building the data passed to the app's handler: [4](#0-3) 

This breaks the identity binding: `HMAC-verified bytes == raw_body` but `shop used downstream != any value covered by that HMAC`. Any body+HMAC pair that is valid for shop A (which an attacker can legitimately obtain by installing the app on their own store and receiving a real webhook) remains valid when replayed with the `shopify-shop-domain`/`x-shopify-shop-domain` header changed to shop B, because the header is not part of the signed content.

### Impact Explanation
This is a cross-tenant data-injection vector: the host application, following this gem's own documented usage (`docs/usage/webhooks.md`, which explicitly says `data.shop` is "The shop domain of the webhook" and shows it being used to key off e.g. `shop_domain: data.shop`), will process attacker-controlled webhook content believing it belongs to a shop the attacker does not control. Depending on how the host app uses `data.shop`/`data.body`, this can lead to writing/overwriting records associated with another merchant's tenant, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only an unprivileged action available to any internet user: installing the target app on a store the attacker controls (a normal, unprivileged OAuth install), capturing one legitimately delivered webhook (body + valid HMAC) for a topic the app handles, and replaying it to the app's public webhook endpoint with an altered `shop-domain` header. No access to `api_secret_key`, tokens, or the victim's credentials is required, since the shared `client_secret` used to sign webhooks is the same for every installation of the app, and the shop field is not part of what is signed.

### Recommendation
Bind the shop identity to the verified signature: either fold `shop-domain` into the HMAC-signed material (not possible unilaterally since Shopify controls the signing scheme), or — more practically for this gem — require/encourage callers to cross-check `request.shop` against a shop that has an active, previously-registered session/webhook subscription (e.g., verify the shop against the app's own persisted list of installed shops) before invoking the handler, and document prominently that `shop` is unauthenticated header data that must be independently validated by the host application prior to trust.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own store "attacker.myshopify.com"
#    and legitimately receives a real webhook, e.g. for "orders/create":
raw_body = '{"id":1,"note":"legit order"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), Context.api_secret_key, raw_body)

headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "attacker.myshopify.com", # original, legitimate
}

# 2. Attacker replays the exact same body/HMAC pair, only changing the shop header
forged_headers = headers.merge("x-shopify-shop-domain" => "victim.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation succeeds because it only checks raw_body, not shop-domain
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle receives WebhookMetadata with shop: "victim.myshopify.com"
#    even though the payload/HMAC were generated for "attacker.myshopify.com"
```

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
