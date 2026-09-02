### Title
Webhook processing trusts `shop-domain`, `topic`, `webhook-id` and `api-version` HTTP headers that are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw HTTP body, while the shop identity (`shop-domain`), the `topic`, `webhook-id`, and `api-version` are read from separate, unsigned HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body-based HMAC and then dispatches the handler using these unauthenticated header values, breaking the intended binding: `HMAC(body) == HMAC(body, secret)` is checked, but the app actually needs `HMAC` to authenticate `(shop, topic, body)` as a tuple, not `body` alone.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only this body-only HMAC via `Utils::HmacValidator.validate(request)`, and then immediately trusts `request.shop` and `request.topic` (taken from headers) to select the handler and construct the metadata handed to app code: [3](#0-2) 

`HmacValidator.validate` in turn only ever signs/verifies `verifiable_query.to_signable_string`, i.e. the raw body: [4](#0-3) 

Because the `shop-domain` header is not part of the signed material, any request whose **body** happens to match a body that Shopify has legitimately signed for the attacker's own store (a `(body, hmac)` pair the attacker legitimately possesses, e.g. from a webhook fired to their own installed app) can be replayed to the host application's webhook endpoint with the `shop-domain` header swapped to a victim shop, and/or the `topic` header changed to a different registered topic. `HmacValidator.validate` will still pass because it never inspects the headers, and `Registry.process` will invoke the handler believing the event genuinely originated from the victim shop / topic.

### Impact Explanation
This breaks the tenant-identity binding the whole webhook signature scheme exists to guarantee: "the shop that receives the event equals the shop that Shopify actually signed the event for." Host applications built on this gem invariably key off `data.shop` (as shown in the gem's own documentation) to decide which merchant's tenant data to mutate — e.g. revoking access tokens on `app/uninstalled`, deleting or exporting merchant data on GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`), or updating billing/subscription state. An attacker who owns any shop that has the target app installed can obtain a validly-signed body/HMAC pair for a topic of their choosing and then relabel it as coming from an arbitrary victim shop domain, causing the host app to perform shop-scoped, credential-impacting actions (e.g. destroying the victim's stored session/access token, disabling their app data, or acting on attacker-supplied JSON as if it were the victim's own webhook payload) — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only an internet-reachable webhook endpoint (which is a documented, expected deployment) and possession of one legitimately-signed `(body, hmac)` pair, obtainable by any attacker who installs the target app on a shop they control (a normal, unprivileged action) and captures the webhook Shopify sends them. No access token, `api_secret_key`, or privileged account is required beyond that. This is a realistic scenario for any Shopify app supporting third-party or public installation.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable material, or otherwise cryptographically bind them to the body before verification, so that `Utils::HmacValidator.validate` fails whenever any of these headers is altered relative to what Shopify actually signed. At minimum, `Request#to_signable_string` should incorporate the shop domain and topic, not just the raw body.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, causing the app to register (e.g.) an `app/uninstalled` webhook.
2. Attacker uninstalls the app, capturing the legitimate webhook HTTP request Shopify sends, including body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Attacker POSTs a forged request to the same webhook endpoint with the same body `B` and hmac header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)`, which still equals `H`, so validation passes.
5. `Registry.process` calls the registered `app/uninstalled` handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to treat this as a legitimate uninstall event for the victim shop (e.g., deleting the victim's stored session/access token), even though the victim never sent this webhook.

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
