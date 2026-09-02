## Finding [1](#0-0) 

### Title
Webhook `shop-domain` is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the HMAC over that same string only. The `shop-domain` header — which is trusted downstream as the tenant identifier for the webhook — is never part of the signed material. Any party that can obtain one authentic `(body, hmac)` pair (e.g., by running the app on their own store and capturing a legitimate webhook delivery) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the request will still pass `HmacValidator.validate`.

### Finding Description
`AuthQuery#to_signable_string` deliberately includes `shop` in the signed payload for the OAuth callback flow [2](#0-1) , correctly binding the shop identity to the HMAC. The webhook path does not do the same: `Webhooks::Request#to_signable_string` only returns `@raw_body`, while `#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read straight from unauthenticated headers [3](#0-2) .

`Registry.process` verifies only this body-based HMAC, then immediately trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The equality that should hold is:
`shop asserted in the request == shop cryptographically bound by the HMAC`

But in this implementation:
`shop asserted in the request (X-Shopify-Shop-Domain header) != anything covered by the HMAC (only raw_body is signed)`

Because the same `api_secret_key` is used for every shop that has installed the app, any store owner (an "unprivileged" actor with respect to other tenants) can legitimately install the app, receive a real webhook (valid `body` + valid `hmac` for their own shop), and then replay that identical `body`/`hmac` pair to the app's public webhook endpoint while swapping in a victim's `X-Shopify-Shop-Domain` value. `HmacValidator.validate` will report the signature as valid (it only checks the body), and `Registry.process` will dispatch the webhook to the handler with `shop: <victim shop>`, `body: <attacker-controlled-but-signed body>`. Any app that persists or acts on `data.shop` from the handler (exactly as documented in `docs/usage/webhooks.md`, where `data.shop`/`data.body` are used to key stored records) will attribute forged/replayed data to the wrong tenant.

Notably, the library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify" [5](#0-4)  — but that guarantee only holds for the body content, not for the `shop` attribution that the handler is told to trust.

### Impact Explanation
This breaks the tenant identity binding for HTTP webhooks: a caller with no privileges on the victim's shop can cause the app to process (and, per the documented handler pattern, persist or act on) data as if it came from a different, victim shop. This is a cross-tenant data-integrity/confusion issue within the gem's own webhook-verification code path (`lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`), matching the "Critical – cross-tenant access" category, since the shop-scoping guarantee that `HmacValidator`/`Registry.process` are supposed to provide is not actually enforced for the field (`shop`) that identifies the tenant.

### Likelihood Explanation
Likelihood is moderate-to-high for any attacker who can install the target app on their own Shopify store (a normal, low-privilege action — no special credentials, access tokens, or secrets are required beyond being any merchant). Once installed, Shopify will deliver at least one genuine webhook with a valid `(body, hmac)` pair to the attacker's own endpoint infrastructure (or the attacker can intercept their own traffic), which they can then replay against the app's public webhook route with a forged `shop-domain` header.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook_id`/`api_version`) header values in the material that is authenticated, or otherwise cryptographically bind the header-derived `shop` to the verified request before it is trusted by `Registry.process`. At minimum, the gem should document/require that the header claim of `shop` not be trusted as tenant identity without an independent recorded association (e.g., verifying the `webhook_id` was actually registered for that shop) before dispatching to handlers, since the current signature scheme provides no cryptographic linkage between the shop header and the signed body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, triggering a legitimate webhook, e.g. `orders/create`. Shopify sends:
   - Headers: `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC of BODY>`
   - Body: `BODY` (JSON payload)
2. Attacker captures `BODY` and the corresponding valid HMAC (they own this store, so this is trivially available to them, e.g. from their own webhook receiver logs).
3. Attacker sends a new HTTP request to the same app's webhook endpoint with:
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <the same valid HMAC captured in step 2>`
   - Body: the same `BODY`
4. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (`= BODY` only) and it matches, so validation passes [6](#0-5) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: <attacker's BODY>, ...)` [4](#0-3) , causing the app to process/store forged data as belonging to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
