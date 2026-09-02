## Title
Webhook `shop-domain` and `topic` headers are trusted by `Registry.process` without being bound to the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body against the app's single, app-wide `api_secret_key`. The `shop-domain`, `topic`, and `webhook-id` values that the handler actually acts on are read from HTTP headers that are never included in the signed content. Because the same `api_secret_key` is shared across every shop that has installed the app, any merchant who has genuinely installed the app can capture one of their own valid `(body, hmac)` pairs and replay it against the app's webhook endpoint with a forged `shop-domain`/`topic` header, causing the app to process attacker-supplied payload data as if it were an authentic webhook for a completely different shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`: [1](#0-0) [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are pulled straight from request headers, entirely outside the signed material: [2](#0-1) 

`Registry.process` verifies the HMAC and then unconditionally trusts those unsigned header values to route and attribute the webhook: [3](#0-2) 

The broken identity binding, as an equality: the code implicitly assumes
`HMAC_valid(body, api_secret_key) ⟺ (shop, topic, webhook_id headers) are authentic for that body`
but the actual guarantee is only
`HMAC_valid(body, api_secret_key) ⟺ body was signed with this app's api_secret_key at some point (for any shop, any topic)`.

Because `api_secret_key` is one value per app (shared by all installed shops), a merchant who legitimately installed the app receives genuine `(body, hmac)` pairs for their own store. That merchant can then send a new HTTP request to the app's webhook endpoint, keeping the same body/hmac but substituting a victim shop's domain in `X-Shopify-Shop-Domain` (and/or an arbitrary `X-Shopify-Topic`). `HmacValidator.validate` still returns `true` because it never looks at the headers, and `Registry.process` dispatches the (attacker-chosen) body to the handler, tagged with the victim's shop and an arbitrary topic of the attacker's choosing.

### Impact Explanation
This breaks the shop/tenant isolation the HMAC check is meant to provide: a merchant using the app is not supposed to be able to inject data attributed to another merchant's shop. Depending on how the host application's webhook handler uses `WebhookMetadata#shop`/`#topic` (e.g., to look up that shop's stored offline session/access token and perform writes, or to trigger mandatory GDPR webhooks like `shop/redact`/`customers/data_request` with attacker-controlled body), this enables cross-tenant data injection/corruption using only a legitimate, unprivileged install of the same app — no leaked credentials or TLS interception required, satisfying the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Any user who can install the app on their own store (an ordinary, unprivileged action) automatically receives valid `(body, hmac)` pairs from Shopify for their own webhooks. Forging the header values and replaying the request requires no secret knowledge and no special access — only the ability to send an HTTP POST to the app's public webhook endpoint, which is by definition internet-reachable. This makes the likelihood high once an attacker has at least one shop connected to the target app.

### Recommendation
Bind the trusted identity fields into the signed material or otherwise cryptographically tie the shop/topic to the signature — e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or independently verify the `shop` header against a known/expected installed shop (e.g., cross-check against a stored session for that shop, and reject if no such session exists) before dispatching. At minimum, the host app should be documented to always verify the shop header corresponds to a shop with an active, known installation before trusting webhook data, and the gem could enforce this by requiring an expected-shop parameter to `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Shopify sends the app a genuine webhook, e.g. topic `customers/data_request`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` and sends their own POST request directly to the app's webhook endpoint with:
   - `X-Shopify-Hmac-Sha256: H`
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <any topic, e.g. shop/redact>`
   - body `B`
4. `Utils::HmacValidator.validate` in `hmac_validator.rb` recomputes the HMAC over `B` using the app's `api_secret_key` — it matches `H` regardless of the header values, since headers are not part of `to_signable_string`.
5. `Registry.process` (`registry.rb` line 190-199) dispatches to the handler with `shop: "victim-shop.myshopify.com"` and the attacker-chosen topic, causing the app to act as though it received an authentic webhook from the victim's shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
