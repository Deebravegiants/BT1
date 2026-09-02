### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw JSON body, then trusts the `shop-domain` HTTP header — which is never included in the signed payload — to identify which merchant/tenant the webhook belongs to. This breaks the identity binding `hmac_signature == HMAC(secret, shop || body)` that a webhook consumer needs; in this gem, the binding actually enforced is only `hmac_signature == HMAC(secret, body)`, independent of `shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor reads directly from the `shop-domain` header with no cryptographic linkage to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC (over body only) and then immediately forwards `request.shop` — an unauthenticated, attacker-controllable field — to the app's handler as the trusted tenant identifier: [3](#0-2) 

Because `shop` is acted upon (dispatched to `WebhookMetadata.shop`, which apps use to key session/token lookups, per the documented `data.shop` usage) but is not covered by the HMAC, an attacker who can obtain any single valid `(raw_body, hmac)` pair signed by Shopify with the app's shared secret — e.g., by owning their own store, installing the target app there, and triggering a webhook — can replay that exact body/HMAC to the app's public webhook endpoint while substituting the `shop-domain` header (and/or `x-shopify-shop-domain`) with a victim shop's domain. `Utils::HmacValidator.validate` will still pass because it only checks the body: [4](#0-3) 

The equality that should hold — "shop authenticated == shop attributed to the event" — is broken: the shop value verified by nothing is the same one acted upon by the handler.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an app relying on this gem's webhook processing to determine which merchant a webhook event pertains to (as the documentation explicitly instructs, e.g. keying session lookup or job dispatch by `data.shop`) can be made to process attacker-supplied body content under a victim shop's identity. Depending on the topic (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`, order/customer webhooks), this can trigger destructive or data-exposing actions attributed to a tenant the attacker does not control, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The attacker only needs a legitimately-signed webhook body+HMAC pair, obtainable trivially by installing the target app on their own (attacker-owned) shop and triggering any subscribed webhook topic — no `api_secret_key`, access token, or privileged account is required. The replay itself only requires sending an HTTP request to the app's public webhook endpoint with a modified header, which is standard unprivileged internet access.

### Recommendation
Bind the shop identity into the signed payload verification: derive the trusted shop either exclusively from a value embedded in the signed body (if Shopify includes it) or require the app to independently verify the `shop-domain` header against an out-of-band trusted source (e.g., cross-check against the topic-specific registered session/webhook subscription for that exact HMAC, or track/consume `webhook_id` values one-time to prevent replay across shops). At minimum, document/require verifying that the resolved `shop` matches a known, currently-installed shop with an active webhook subscription for the given `webhook_id`/topic combination before trusting `WebhookMetadata.shop`, and warn against using the header-derived `shop` value as a sole tenant key when the header is not covered by `to_signable_string`.

### Proof of Concept
1. Attacker installs the target app on shop `attacker.myshopify.com`, triggering a webhook the app is subscribed to (e.g. `orders/create`).
2. Shopify sends the app a POST with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures this exact `(B, HMAC)` pair.
4. Attacker replays the identical request to the app's webhook endpoint, only changing `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
5. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) recomputes HMAC over `to_signable_string` (`= @raw_body`, unchanged) and it matches — validation passes.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the app to process attacker-controlled body content as if it originated from the victim shop.

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
