## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing / cross-tenant webhook injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives its `shop` (and `topic`, `api_version`, `webhook_id`) values from HTTP headers, but the HMAC signature that `Utils::HmacValidator.validate` checks is computed only over the raw request body via `to_signable_string`. The header that identifies *which tenant* the webhook belongs to is never part of the signed data, so a valid signature says nothing about which shop the payload actually came from.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` is read straight from the unauthenticated `x-shopify-shop-domain` (or `shopify-shop-domain`) header: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `request.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e. only the body, never the shop header: [3](#0-2) 

`Registry.process` trusts this unauthenticated `shop` value as the tenant identity and hands it straight to the app's webhook handler: [4](#0-3) 

**Binding broken (as an equality):** the gem should guarantee `hmac_signed(shop) == shop_used_for_routing`, but instead it only guarantees `hmac_signed(raw_body) == raw_body`, while `shop_used_for_routing` comes from an independent, unsigned header. An attacker who possesses *any* valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` — which every merchant naturally receives the moment Shopify sends them a real webhook after installing the app — can replay that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it never inspects that header, and `Registry.process` will invoke the app's handler with `WebhookMetadata` attributing the (attacker-supplied) body to a victim shop of the attacker's choosing.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: a normal, unprivileged app-installer (any merchant who installs the app gets a legitimately signed webhook) can forge webhook deliveries "from" any other shop domain, since the signature never binds to the shop. Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g., `shop/redact`, `customers/redact`, `app/uninstalled`), this enables cross-tenant data operations, false uninstall/redaction triggers against a shop the attacker doesn't own, or injection of forged data attributed to another merchant — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires no privileged credentials, only the ability to install the app as a normal merchant (to obtain one legitimately signed webhook body+hmac) and to send an HTTP POST to the app's public webhook endpoint with a modified header — well within reach of an "unprivileged internet user."

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed material that `HmacValidator` verifies, or otherwise independently authenticate the `shop` value (e.g., cross-check it against a shop known to be associated with the session/app installation) before using it to route or act on webhook data in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`. Shopify sends a legitimate webhook, e.g. `customers/redact`, to the app's webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`.
2. Attacker captures the raw body and HMAC.
3. Attacker replays the exact same POST body and `x-shopify-hmac-sha256` value to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` invokes the registered handler with `shop: request.shop` equal to `victim.myshopify.com` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to perform whatever shop-scoped action (e.g., data redaction, uninstall handling) the webhook triggers against the victim tenant instead of the attacker's own shop.

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
