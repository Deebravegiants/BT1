This confirms the vulnerability. Now I have enough detail to write the finding.### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by HMAC verification, allowing cross-tenant replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using `shop`, `topic`, and `webhook_id` values taken from HTTP headers that are never included in the signed bytes. An unprivileged internet user who has received (or intercepted) any single legitimately-signed webhook delivery for a given app can replay that exact body/HMAC pair while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` header values, causing the host application's webhook handler to process attacker-chosen tenant/topic metadata as if Shopify had sent it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead read directly from HTTP headers that are not part of the signable string at all: [2](#0-1) .

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)` — which only re-computes and compares the HMAC over `to_signable_string` (the raw body) — and then immediately trusts `request.topic`, `request.shop`, and `request.webhook_id` to look up the handler and build the `WebhookMetadata` passed to it: [3](#0-2) . `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it only to the `hmac` field; it has no knowledge of `shop`/`topic`/headers: [4](#0-3) .

This breaks the intended identity binding:
`signed_bytes (raw_body + hmac) == trusted_identity (shop, topic, webhook_id)`
In reality, the verified bytes are only `raw_body`, while `shop`, `topic`, and `webhook_id` are unauthenticated header values parsed independently — i.e. "bytes verified" ≠ "bytes/fields acted on downstream." Because the same `client_secret` is used to sign every webhook for every shop that installs the app, a valid `(raw_body, hmac)` pair obtained from any one delivery (e.g., a webhook sent to the attacker's own installed/dev store) remains a cryptographically valid pair regardless of which `shop-domain`, `topic`, or `webhook_id` header accompanies it, since none of those fields are covered by the signature. This is confirmed by the test suite itself, which builds the HMAC purely from the JSON body `"{}"` and freely varies headers between the legacy `x-shopify-*` and new `shopify-*` formats while keeping the same HMAC: [5](#0-4)  and [6](#0-5) .

### Impact Explanation
The `shop` value from `WebhookMetadata` is documented as the authoritative per-tenant identifier host apps use to route data ("The shop domain of the webhook"): [7](#0-6) , and `WebhookHandler#handle` receives it as the only tenant-scoping field: [8](#0-7) . Any host application that trusts `data.shop`/`data.topic` for tenant/topic dispatch (as the gem's own documented example does — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to attribute a replayed, cryptographically "valid" webhook body to an attacker-chosen shop and topic, achieving cross-tenant data injection without possessing the app's `client_secret`. This satisfies the Critical bar of "cross-tenant access" since the tenant-binding check the gem performs (`Utils::HmacValidator.validate`) never actually covers the tenant-identifying field it hands to the handler.

### Likelihood Explanation
Exploitation requires only a single legitimately delivered webhook body+HMAC pair, obtainable by any developer/attacker who installs the app on their own store (a normal, unprivileged action) or intercepts one delivery over a non-TLS-terminated proxy the attacker controls, then replays that exact body to the app's public webhook endpoint with modified headers. No access to `api_secret_key`, access tokens, or the merchant's environment is required — only network reachability to the webhook endpoint, which by design is publicly accessible without authentication.

### Recommendation
Bind the identity fields into the signed representation, or otherwise re-verify them out-of-band: extend `Request#to_signable_string` (or add a second check) so that `shop`, `topic`, and `webhook_id` are validated against Shopify's actual behavior — e.g., cross-check `request.shop` against a known/allow-listed set of installed shops for the app and reject any topic/shop/webhook_id combination that Shopify would not have produced for that specific `webhook_id`, and/or document loudly that `WebhookMetadata#shop`/`#topic` are **not** cryptographically bound to the HMAC and must be independently validated by host applications (e.g., against `Registry`'s own registration state or a webhook_id de-duplication ledger) before being used for tenant routing.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, triggering a legitimate webhook, e.g. `orders/create`, with body `B` and Shopify-computed `X-Shopify-Hmac-Sha256: H` (valid for the app's single global `client_secret`).
2. Attacker replays the exact same `B`/`H` to the app's webhook endpoint but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: customers/redact` (or any other registered topic)
   - `X-Shopify-Webhook-Id: <arbitrary>`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds, matching the code path shown in [9](#0-8) .
4. The handler receives `WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: <parsed B>, ...)` and processes it as if Shopify had authoritatively reported this event for `victim-shop.myshopify.com`, even though no data for that shop was ever involved.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** test/webhooks/registry_test.rb (L16-30)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```

**File:** test/webhooks/registry_test.rb (L284-299)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
