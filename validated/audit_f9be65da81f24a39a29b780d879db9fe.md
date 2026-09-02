### Title
Webhook shop-tenant identity spoofing via `shop-domain` header not covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw JSON body, then unconditionally trusts the `shop-domain` header to identify which merchant/tenant the payload belongs to. Because the header is never part of the signed material, an attacker who can obtain one legitimate `(body, hmac)` pair for a webhook — for example by installing the app on their own store, a routine unprivileged action — can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, causing the host application to process the payload as belonging to a different, victim tenant.

### Finding Description
`Registry.process` performs a single check before dispatching to the handler: [1](#0-0) 

The HMAC check calls into `Utils::HmacValidator.validate`, which validates `request.to_signable_string` against the shared `api_secret_key`: [2](#0-1) 

`Webhooks::Request#to_signable_string` returns only `@raw_body`, never the headers: [3](#0-2) 

Meanwhile `Webhooks::Request#shop` — the value later placed into `WebhookMetadata.shop` and handed to the app's handler as the authoritative tenant identifier — is read directly, unauthenticated, from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header: [4](#0-3) 

The identity binding that the library implicitly promises — “the shop that the HMAC-validated body is attributed to” — is never enforced. The equality `hmac_signer_intended_shop == request.shop_header` does not hold: the signature only proves “this exact byte sequence body was countersigned by an entity that received it from Shopify for *some* installation of this app,” while `shop` is an independent, unsigned field parsed straight from attacker-controlled HTTP headers. Since `api_secret_key` is the app's single client secret shared across every merchant installation (not a per-shop key), any merchant/attacker who installs the app legitimately receives real `(body, hmac)` pairs for their own store's webhooks and can freely relabel them with a victim shop's domain when POSTing to the app's webhook endpoint.

The gem's own documentation reinforces the expectation that `data.shop` is a trustworthy field once `Registry.process` succeeds — it is documented simply as "The shop domain of the webhook" with no caveat that it is unauthenticated: [5](#0-4) 

### Impact Explanation
This breaks the shop/tenant identity binding and enables cross-tenant confusion in every consuming application, including the mandatory GDPR topics the gem itself registers by default (`shop/redact`, `customers/redact`, `customers/data_request`): [6](#0-5) 

An attacker with their own (legitimately installed) shop can forge webhooks attributed to a victim shop — e.g., trigger `customers/redact` processing, order/product state changes, or any topic-specific side effects — against a tenant record that is not theirs, since the host app's persistence layer keyed by `data.shop` has no way to distinguish this from a genuine Shopify-originated event for that shop. This is a cross-tenant access vulnerability rooted entirely in this gem's webhook verification design.

### Likelihood Explanation
Exploitation requires only: (1) installing the app on an attacker-controlled development/test store (a normal, unprivileged action any internet user can perform for public apps), (2) capturing one legitimate webhook `(raw_body, hmac)` pair Shopify sends for that store, and (3) resending it with a substituted `shop-domain` header to the app's webhook callback URL, which is a publicly known/discoverable route. No access to `api_secret_key`, tokens, or the victim's credentials is needed.

### Recommendation
Do not treat `shop-domain` as trusted purely because the body HMAC validates. Either (a) include the shop domain in the signed material used for `to_signable_string` (mirroring what `Auth::Oauth::AuthQuery` does by including `shop` in its signable string, per `lib/shopify_api/auth/oauth/auth_query.rb`), or (b) require/document that consuming applications must cross-check `request.shop` against the shop for which the webhook topic was registered/expected (e.g., via a known active session for that shop) before acting on the payload, and make this an explicit, enforced step in `Registry.process` rather than leaving it as an undocumented caller responsibility.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, obtaining a real `access_token`/session and causing the app to register webhooks (e.g. `customers/redact`) for that shop.
2. Shopify sends a genuine webhook to the app's callback URL with body `B` and header `X-Shopify-Hmac-SHA256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` (e.g. via their own reverse proxy/logging on their dev endpoint, or by triggering the webhook and observing it in transit to their own server) and replays it to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(api_secret_key, B) == H` — unaffected by the header change: [7](#0-6) 
5. The handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, causing the host application to act on the victim tenant using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
