### Title
Webhook shop identity spoofing — `shop` header excluded from HMAC signature verification - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from only the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read from unauthenticated HTTP headers and forwarded to the host application's webhook handler as if they were verified. This breaks the identity binding `shop_authenticated == shop_used_as_tenant_key`, since the HMAC never covers the shop domain that downstream code trusts to select the tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

`Registry.process` relies solely on this HMAC check to decide the webhook is authentic, then builds `WebhookMetadata` using `request.shop`, which is read verbatim from the `x-shopify-shop-domain`/`shopify-shop-domain` header — a value that was never part of the signed bytes: [3](#0-2) [4](#0-3) 

Because the `api_secret_key` used for HMAC validation is the app's single shared client secret (not per-shop), any merchant who installs the app receives legitimately-signed webhooks for their own store. Nothing in `Request`, `HmacValidator`, or `Registry` binds the verified body to the specific `shop` header claimed in that same request — the header can be freely substituted without invalidating the HMAC, since it's outside the signed payload.

The gem's own documented usage pattern encourages host apps to key their tenant data directly off this unverified field: [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity confusion analogous to the reported bug class (an identity value acted upon but not covered by the integrity check). An attacker who is a legitimate (if malicious) merchant can take a webhook payload that Shopify genuinely signed for their own store and resubmit it to the app's webhook endpoint with the `shop` header rewritten to a victim shop's domain. The HMAC still validates (it never covered the header), so `Registry.process` accepts the request and calls the handler with `WebhookMetadata#shop` set to the victim's domain while `body` is fully attacker-controlled. Any host application that uses `data.shop` to select which tenant's record to update (the pattern the gem's own docs recommend) will attribute attacker-controlled data to the victim shop — a cross-tenant data injection driven entirely by this gem's incomplete verification.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the target app on any shop they control (an "unprivileged internet user" relative to other merchants' data) and be able to POST arbitrary HTTP headers to the app's public webhook endpoint — no access to `api_secret_key`, access tokens, or any other merchant's credentials is needed.

### Recommendation
Include the shop domain (and other identity-bearing headers such as topic/webhook-id/api-version) in the HMAC-signed payload used by `Request#to_signable_string`/`HmacValidator`, or otherwise cryptographically bind the header-derived `shop` value to the signed body before exposing it via `WebhookMetadata`. At minimum, document prominently that `data.shop` from `WebhookMetadata` is not covered by HMAC verification and must not be trusted as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a body they control.
2. Shopify sends the webhook to the app's endpoint with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's shared secret, and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts/replays this exact request but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`, leaving body and HMAC header untouched.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.to_signable_string` (`@raw_body`) against the HMAC header — see [6](#0-5) .
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)` and, following the gem's documented pattern, writes attacker-controlled data into the victim shop's tenant record.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
