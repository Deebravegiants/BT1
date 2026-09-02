### Title
Webhook `shop` domain is not covered by the HMAC signature but is trusted as tenant identity - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then forwards the `shop-domain` header — which is *not* part of the signed material — to the app's handler as the trusted tenant identifier.

### Finding Description
The identity binding that should hold is:
`bytes verified by HMAC == bytes the application acts on as the tenant identity`.

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the signature purely against that signable string: [2](#0-1) 

`Registry.process` gates handling only on this body HMAC, then reads `request.shop` (sourced from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) and passes it straight into `WebhookMetadata` as the tenant identity delivered to the app's handler: [3](#0-2) [4](#0-3) 

So the `shop` field that the host application will use to look up/act on a tenant record is acted upon (`data.shop`) but is not covered by the HMAC (only `@raw_body` is signed). Anyone who can obtain one legitimately-signed webhook body/HMAC pair for their own shop (any unprivileged merchant can install a public app on their own store and receive real Shopify webhooks with a valid HMAC computed with the app's shared secret) can replay that same body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (e.g. a victim merchant's domain). `HmacValidator.validate` will still return `true` because the header is irrelevant to the signature check, and the handler will process the (attacker-controlled) body under the victim's shop identity.

### Impact Explanation
This breaks the tenant/shop authentication boundary — the equality "HMAC-verified bytes == bytes used for tenant attribution" does not hold, because the `shop` field is excluded from the signable string. Depending on how the host app's webhook handlers use `data.shop` (e.g., to update per-shop state, create records, or trigger per-shop side effects), this enables cross-tenant data injection/confusion: an attacker-controlled event body can be attributed to and processed against a shop the attacker does not own or control, without needing the app's `client_secret`/`api_secret_key`. This matches the Critical "cross-tenant access" bucket.

### Likelihood Explanation
Exploitability depends entirely on the host application trusting `data.shop` (as returned by this gem) without independently verifying it belongs to a shop the app has installed/authenticated a session for. This mirrors Shopify's actual webhook HMAC design (Shopify itself only signs the raw body, not headers), so this is an inherent characteristic of the protocol that this gem faithfully implements rather than a bug this gem introduces — the library does not additionally validate or expose the header/body binding, and its documentation does not surface this caveat within the reviewed `lib/shopify_api/webhooks/**` and `lib/shopify_api/utils/**` code. I was not able to fully confirm from the indexed code whether `docs/usage/webhooks.md` (out of scope per the rules) explicitly warns integrators to cross-check `data.shop` against a known/installed shop before trusting it, which would materially reduce likelihood if host apps follow that guidance.

### Recommendation
- Have `Webhooks::Request` and/or `HmacValidator` bind the `shop-domain` (and `topic`) header into the signable material used for verification (e.g., derive/verify shop identity as part of the check, or explicitly document/enforce that `data.shop` must be cross-checked by the caller against a stored, previously-authenticated session for that shop before any tenant-scoped action is taken).
- At minimum, make this exclusion explicit and prominent in the gem's public API/docs (e.g., a code comment and `WebhookMetadata` doc note) so integrators do not treat `shop` as authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with header `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends this exact HTTP request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (leaving the body and HMAC header untouched).
3. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only [5](#0-4)  and it still matches, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: attacker_controlled_body ...)` [6](#0-5) .
4. If the host application's webhook handler uses `data.shop` to select the tenant record to update (a common, natural usage pattern), the attacker has caused attacker-controlled data to be processed under `victim-shop`'s identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
