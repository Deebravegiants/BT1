### #Title
Webhook Shop/Topic Identity Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop`, `topic`, and `webhook_id` fields—used by the gem to route and attribute the webhook to a tenant—come from HTTP headers that are never included in the signed data. This is the same class of bug as the Golem `batchTransfer` finding: a value that is used operationally to determine ownership/identity (`balances[addr]` recipient / here, the tenant `shop`) is not bound to the same authenticated context (the loop's running `balance` / here, the HMAC signature), so it can be manipulated independently of the verified data.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are read straight from headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` verifies the signature only against `verifiable_query.to_signable_string`, i.e., the raw body: [3](#0-2) 

`Registry.process` then trusts `request.shop` unconditionally and hands it to the app's webhook handler as the tenant identity, with no re-derivation from anything HMAC-covered: [4](#0-3) 

Because the HMAC only proves "this body byte sequence was produced with the app's secret at some point," and never proves "this body belongs to shop X," anyone who can obtain one validly-signed webhook body/HMAC pair (e.g., by triggering a webhook on their own, unprivileged, installed store) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header for a victim shop. `HmacValidator.validate` will still pass because it never inspects those headers, and `Registry.process` will invoke the handler with `shop: <victim>` even though the body content is entirely attacker-controlled.

The broken identity-binding equality is:
`bytes verified (raw_body only)` ≠ `bytes/fields acted on (shop, topic, webhook_id headers)`.

### Impact Explanation
This breaks the shop/tenant boundary the gem exists to enforce for embedded apps: a request whose payload originates from a low-privilege attacker's own shop can be attributed by the library to an arbitrary victim shop. Depending on how host applications key their persistence on `WebhookMetadata#shop` (which is the norm, since that's the field this gem exposes precisely for that purpose), this enables cross-tenant data injection/corruption — e.g., writing attacker-controlled order/customer/app-uninstall data against a victim shop's record. This falls under "cross-tenant access," a Critical-tier impact per the report's own required categories.

### Likelihood Explanation
Exploitation requires no credentials beyond ordinary control of one's own Shopify store (installing the target app on it to receive a genuine, correctly-HMAC-signed webhook), and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with attacker-chosen headers — both trivially available to an unprivileged internet user. No access token, `client_secret`, or privileged account is needed, since the HMAC is only ever validated against the body, and the header manipulation happens entirely on the attacker's own outbound replayed request.

### Recommendation
Bind the shop/topic identity into the verified data rather than trusting headers unconditionally:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (matching Shopify's actual signing scope), or
- At minimum, require the host application/gem to cross-check the header-derived `shop` against an independently authenticated channel (e.g., only accept webhooks over a per-shop secret/URL, or validate the shop against a known list of currently installed shops) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g., `orders/create`) with attacker-controlled body content.
2. Attacker captures the resulting raw body and the valid `X-Shopify-Hmac-Sha256` value Shopify computed for that body.
3. Attacker sends a POST to the app's webhook endpoint with:
   - the exact same raw body and `x-shopify-hmac-sha256`,
   - `x-shopify-shop-domain: victim-shop.myshopify.com`,
   - `x-shopify-topic` set to whatever topic the app expects.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only checks the raw body.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's chosen body, causing the host app to process attacker data as if it came from the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
