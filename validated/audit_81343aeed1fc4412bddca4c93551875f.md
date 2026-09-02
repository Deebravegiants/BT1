### Title
Webhook HMAC signs only the request body, letting the unauthenticated `shop`/`topic` headers be swapped to spoof cross-tenant webhook events - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so the HMAC verified by `Utils::HmacValidator` never covers the `shop`, `topic`, `webhook-id`, or `api-version` headers. `Registry.process` trusts `request.shop`/`request.topic` taken straight from these unauthenticated headers when building the `WebhookMetadata` handed to the host app's handler, breaking the binding between "body cryptographically authenticated as coming from Shopify" and "shop the body is attributed to."

### Finding Description
The webhook signature check is: [1](#0-0) 

and it validates against `verifiable_query.to_signable_string`, which for webhooks is defined as: [2](#0-1) 

Only `@raw_body` is signed. The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [3](#0-2) [4](#0-3) 

`Registry.process` only checks the HMAC over the body and then forwards the unauthenticated `request.shop`/`request.topic` values directly into `WebhookMetadata`, which is what the host application uses to key its tenant data: [5](#0-4) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that has installed the app, any merchant who installs the app on their own store receives webhook deliveries that are genuinely HMAC-signed with that same shared secret for content they fully control (e.g. by editing a product to trigger `products/update`, or subscribing with permissive `fields`/`filter`). That merchant can capture a valid `(raw_body, hmac)` pair from their own legitimate delivery and replay it to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header with an arbitrary victim shop domain. `HmacValidator.validate` recomputes `HMAC(secret, raw_body)` and compares only that — it is unaffected by header changes, so the forged request passes validation. `Registry.process` then calls the app's handler with `shop: <victim-domain>`, `topic: <attacker-chosen-topic>`, and `body: <attacker-controlled JSON>`, exactly as if Shopify itself had sent this event for the victim shop.

This is the report's bug class ("field acted on but not covered by the signature") mapped onto webhook processing: the equality the code should enforce is `shop_the_hmac_authenticates == shop_the_app_acts_on`, but the HMAC authenticates nothing about `shop` at all — only the body.

### Impact Explanation
An unprivileged merchant (anyone who can install the app on their own store — no special privilege, no access to `api_secret_key`, access tokens, or victim credentials) can inject arbitrary attacker-controlled webhook events attributed to any other shop's tenant. Depending on how the host app's handlers use `WebhookMetadata#shop` (most apps key their per-shop data/state directly off this field, as documented in `docs/usage/webhooks.md` and `BREAKING_CHANGES_FOR_V15.md`), this enables cross-tenant data injection/corruption — e.g. spoofing `app/uninstalled`, `shop/redact`, `customers/redact`, or `orders/create` for a victim shop, causing the app to delete/mutate/create records for a tenant the attacker never installed on or authenticated against. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high relative to the report's own "Low" severity ceiling: no secrets are required, the attacker only needs (a) their own installation of the target app (freely obtainable for any public app) and (b) the ability to POST arbitrary HTTP headers to the app's public webhook endpoint, which is by design internet-reachable. Capturing a valid `(body, hmac)` pair requires no special access — it's simply a webhook the attacker receives for actions on their own store.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed content used for HMAC verification, or otherwise cryptographically bind them to the payload (e.g. verify the `shop` in the header against the `shop` returned by exchanging/validating the delivery via Shopify's API, or require the app to independently confirm the shop is one it has an active session/registration for before trusting `WebhookMetadata#shop`). At minimum, `Utils::HmacValidator`/`Webhooks::Request#to_signable_string` should not allow header values that materially affect tenant attribution to bypass signature coverage.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers for `products/update`.
2. Attacker edits a product, triggering Shopify to send a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)` — this is genuinely signed with the app's shared `api_secret_key`.
3. Attacker intercepts/replays this request to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (leaving body `B` and `H` unchanged).
4. `HmacValidator.validate` recomputes `HMAC(secret, B)`, matches `H`, and passes — see [6](#0-5) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata(shop: "victim.myshopify.com", topic: "products/update", body: B, ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop — see [7](#0-6)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
