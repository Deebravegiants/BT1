### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" [1](#0-0)  and hands the verified request's `shop` field straight to the app's handler as the trusted tenant identifier [2](#0-1) . However, the HMAC verification only covers the raw request body, not the `shop-domain` header that supplies this identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

`shop` is read independently, directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, with no cryptographic tie to the signed body: [4](#0-3) 

`Utils::HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the `hmac-sha256` header: [5](#0-4) 

`Registry.process` uses this validation result as the sole authentication gate before dispatching the (header-derived, unauthenticated) `request.shop` value straight into `WebhookMetadata` for the app's handler: [2](#0-1) 

The gem's own documentation instructs apps to key their persisted data directly off `data.shop` (e.g. `shop_domain: data.shop`) after calling `Registry.process`, describing the call as verifying "the request did indeed come from Shopify": [6](#0-5) [1](#0-0) 

The identity binding that is broken is:
`shop authenticated by HmacValidator.validate(request)` ≠ `shop stored/acted upon in WebhookMetadata.shop`

Because the app's `client_secret`/`api_secret_key` is a single shared secret used to sign webhooks for **every shop** that has the app installed (not a per-shop secret), any shop that has the app installed can legitimately receive from Shopify a `(raw_body, hmac)` pair signed with that shared secret. Since `shop-domain` is not part of the signed material, that same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with an arbitrary, attacker-chosen `x-shopify-shop-domain` header naming a different (victim) shop. `HmacValidator.validate` still returns `true` because it never looks at the header, and the handler receives `WebhookMetadata` claiming the event is for the victim shop.

### Impact Explanation
This is a cross-tenant access/data-integrity break: a merchant who is an ordinary, unprivileged user of the app (no access to `api_secret_key`, no privileged account, no TLS interception) can forge webhook events attributed to another merchant's shop. Since apps are documented to use `data.shop` as the tenant key for storage/side-effects, this can corrupt or exfiltrate cross-tenant state (e.g. writing attacker-controlled order/product/customer data into another shop's records, or triggering shop-scoped business logic under an incorrect tenant). This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Likelihood is significant for any app that has more than one shop installed (the common case for any published app), since:
- The attacker only needs their own, ordinary installation of the app (no elevated privilege).
- They passively observe a legitimately Shopify-signed webhook delivered to their own endpoint (or capture one via any standard HTTP tooling) and replay the same body/HMAC to the same endpoint with a modified `X-Shopify-Shop-Domain` header — no cryptographic material needs to be recovered.
- Nothing in `Registry.process` or `HmacValidator` rejects a replayed, header-mismatched request.

### Recommendation
Bind the `shop` claim into the value that is HMAC-verified — e.g., verify the `shop-domain` header against a shop known to be actively installed and previously associated with a stored session/webhook registration ID before dispatching to the handler, or include the shop domain in the signable material used for verification. At minimum, the gem should document explicitly that `data.shop` is *not* authenticated by the HMAC check and must be independently cross-checked by the host app against its own known installed-shops list.

### Proof of Concept
1. App `MyApp` is installed on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com` (both share the same `api_secret_key`).
2. Shopify delivers a legitimate webhook to the attacker's shop:
   - Body: `{"id": 1}`
   - Headers: `x-shopify-hmac-sha256: <valid HMAC of body with shared secret>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
3. Attacker captures this exact `(body, hmac)` pair and re-sends it to the app's public webhook endpoint, replacing only the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `hmac == HMAC(raw_body, secret)`, which is unchanged. [7](#0-6) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id": 1}, ...)`, and per the documented handler pattern the app persists/acts on this data keyed by `victim-shop.myshopify.com`, even though it never originated from that shop. [8](#0-7)

### Citations

**File:** docs/usage/webhooks.md (L20-30)
```markdown
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
