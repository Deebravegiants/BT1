### Title
Webhook shop identity not bound to HMAC signature enables cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as authenticated for a given shop as soon as `Utils::HmacValidator.validate(request)` passes, then hands the handler a `WebhookMetadata` built from `request.shop`, which is read straight from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header. That header is never included in the signable content used to compute the HMAC, so the equality the gem implicitly asserts — "HMAC valid ⇒ this shop sent this body" — does not actually hold.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`HmacValidator.validate` computes/verifies the signature purely over that signable string with the app's `api_secret_key`: [2](#0-1) 

The shop identity is a completely separate accessor that just reads an attacker-controlled header, with no cryptographic tie to the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity for the handler: [4](#0-3) 

The broken binding, stated as an equality:
- Verified: `HMAC == HMAC_SHA256(api_secret_key, raw_body)`
- Trusted/acted-on: `shop == headers["shopify-shop-domain"]`

Because `shop` is outside the HMAC-covered bytes, any request that carries a *previously valid* `(raw_body, hmac)` pair can be replayed with an arbitrary `shopify-shop-domain` header and will still pass `HmacValidator.validate`. An unprivileged internet user can obtain such a valid `(raw_body, hmac)` pair simply by installing the target app on their own store (a normal, self-service action requiring no special privilege) and letting Shopify deliver a real webhook to the app's endpoint. The attacker then replays that exact body/HMAC to the same public webhook endpoint while swapping the shop-domain header to a victim shop, causing `Registry.process` to dispatch the handler with `shop: <victim shop>` even though the body/HMAC were never associated with that shop.

### Impact Explanation
This crosses a tenant boundary within the gem's own webhook-processing code: the app's per-shop webhook handling logic (registered via `Registry.add_registration`) receives attacker-chosen shop identity alongside attacker-replayed (but Shopify-HMAC-valid) payload data, without any code path in the gem re-deriving or checking that `shop` is consistent with the signed bytes. Any host application relying on the gem's stated guarantee — that a webhook passing HMAC validation belongs to the shop named in `WebhookMetadata#shop` — is exposed to cross-tenant confusion (e.g., writing/deleting per-shop state keyed by the spoofed shop domain, or processing mandatory compliance topics like `customers/redact` against the wrong shop). This falls under "cross-tenant access," a Critical-severity impact.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker needs to obtain one genuine `(raw_body, hmac)` pair, which is achievable without any special access by simply installing the app on an attacker-owned store and triggering any subscribed webhook topic (e.g., `orders/create`). No `api_secret_key`, access token, or TLS interception is required — only normal, self-service interaction with the app as a merchant, followed by a direct HTTP replay to the app's public webhook endpoint with a modified header.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the HMAC-verified material, or otherwise cryptographically tie the trusted shop value to the signed body before it is handed to handlers — e.g., require the host application/gem to cross-check `request.shop` against a shop value embedded in the JSON payload itself (Shopify webhook payloads typically include shop-scoped identifiers), or reject processing when the header-derived shop cannot be corroborated by verified, shop-scoped data. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and lets it complete OAuth normally.
2. Attacker triggers a subscribed webhook topic (e.g. creates an order) and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent to the app's webhook endpoint — both are valid because they were genuinely computed by Shopify with the app's real secret.
3. Attacker resends the identical body and HMAC header to the same public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Webhooks::Request.new` parses the forged headers; `HmacValidator.validate` recomputes the HMAC over the unchanged raw body and it matches, so `Registry.process` calls the handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: ..., ...)`, even though `victim.myshopify.com` never sent this request: [5](#0-4)

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
