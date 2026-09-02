### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant impersonation - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used for tenant routing purely from the unauthenticated `shopify-shop-domain` HTTP header, while the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. This breaks the identity binding `shop_authenticated == shop_bound_by_signature`, allowing an attacker who possesses one *valid* signed webhook body (e.g., from their own shop installation of the app) to relabel it as coming from a different shop and have it accepted as authentic by `Registry.process`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string` (i.e., the raw body only): [3](#0-2) 

`Registry.process` trusts the HMAC check and then forwards the unauthenticated `request.shop` value directly into the tenant-identifying `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the signature never covers the `shop-domain` header, `shop` is effectively an attacker-controlled label attached to a cryptographically valid message. Any party who can obtain one legitimately-signed webhook body/HMAC pair (for instance a merchant who installs the app on their own store and triggers an event to receive a real webhook for their own body content) can replay that exact `raw_body` + `hmac` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` (it never inspected the shop header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to a different shop.

### Impact Explanation
This crosses a tenant boundary without any credential of the target shop: an attacker can cause the host application to process/store data under the identity of a shop they do not control, as long as the app's webhook handler relies on `WebhookMetadata#shop` (as documented/intended by this gem) to route/attribute data. This matches the Critical/High "cross-tenant access" category, since the shop identity — the equivalent of the ERC20 allowance owner check in the external report — is asserted from unauthenticated data instead of being bound to the verified signature.

### Likelihood Explanation
Likelihood is realistic but not trivial: the attacker needs at least one valid `(raw_body, hmac)` pair signed by the app's `api_secret_key`. The most direct way to obtain one without leaking the secret is to be a legitimate (even free-tier) merchant who installs the target app, which causes Shopify to send the attacker real signed webhooks for their own shop. The attacker can then replay that captured body/HMAC to the app's public webhook endpoint with a forged `shop-domain` header, requiring no interception of TLS traffic and no possession of the secret itself — only observation of webhooks their own store legitimately receives.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed payload verification, e.g. by rejecting the request if the previously-registered/expected shop for that HMAC doesn't match, or by requiring the host application to cross-check `request.shop` against a known list of shops that have installed the app before trusting it for any tenant-scoped operation. At minimum, document prominently in `WebhookMetadata`/webhook processing that `shop` is unauthenticated header data and must be independently verified against the app's own installed-shop records before being used for tenant-scoped lookups or writes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and triggers any webhook event, capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sent (a genuinely valid signature for `B`).
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - `raw_body = B` (unchanged)
   - `X-Shopify-Hmac-Sha256 = H` (unchanged)
   - `X-Shopify-Shop-Domain = victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic` set to whatever topic matches `B`'s original topic (also forgeable, unsigned).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only, which matches `H`, so validation passes.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though the payload actually originated from the attacker's own shop — demonstrating the shop attribution is not cryptographically bound.

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
