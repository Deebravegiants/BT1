### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body [1](#0-0) , while the `shop` identity used by the rest of the pipeline is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` only checks `hmac == HMAC(body, secret)` [3](#0-2) , so it can never detect that the `shop` header was swapped. `Registry.process` trusts this unverified `shop` value and forwards it to the app's handler as the tenant identity [4](#0-3) .

### Finding Description
The identity binding that should hold is:
`shop header used to attribute the webhook == shop that the HMAC-signed bytes actually originated from`

This binding is broken. The HMAC only signs `@raw_body` [1](#0-0) ; it never signs `shop`, `topic`, `webhook-id`, or `api-version`. The client_secret used to compute the HMAC is per-app, shared across every shop that installs the app — it is not per-tenant. Consequently, any body+HMAC pair that was legitimately generated for shop A remains a valid signature no matter what `shop-domain` header accompanies it.

An unprivileged internet user who has legitimately installed the target app on their own store (a normal, unprivileged action — installing an app requires no special privilege) receives real webhook deliveries with a valid `raw_body` and `hmac-sha256` header signed by the app's real `client_secret`. Because the signature never binds to the shop, that same `(raw_body, hmac)` pair can be replayed to the same webhook endpoint with the `shop-domain` header rewritten to point at a different, victim shop. `Utils::HmacValidator.validate` will still return `true` because it only re-derives the HMAC from the body [5](#0-4) , and `Registry.process` will hand the handler a `WebhookMetadata` object whose `shop:` field is the attacker-controlled header value [6](#0-5) .

Before the attack: `request.shop == <attacker's own store>` for the body/HMAC pair they captured.
After the attack: `request.shop == <victim store>` while the HMAC-verified bytes are unchanged — the equality the gem is implicitly relying on (`verified body ⇒ verified shop`) no longer holds.

### Impact Explanation
This crosses a tenant boundary using only credential-free replay: an attacker with a normal (their own) install can inject fabricated webhook payloads that the host application will process as if they came from a different merchant's shop (e.g. forged `orders/create`, `app/uninstalled`, `customers/data_request`, etc., attributed to the victim's shop id). Any app logic keyed off `WebhookMetadata#shop` (data storage, GDPR redaction triggers, order sync, uninstall handling) can be poisoned or triggered for a tenant the attacker does not control. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high given the low bar to exploit: the attacker only needs a legitimate install of the target app in their own store (available to any unprivileged internet user who can install a Shopify app) to obtain a valid `(raw_body, hmac)` pair, then can freely rewrite the `shop-domain` header on replay — no access to `client_secret`, tokens, or the victim's credentials is required.

### Recommendation
Bind the shop identity into the trust boundary of webhook verification rather than trusting the raw header value:
- Cross-check `request.shop` against the shop associated with the specific webhook registration/subscription (e.g., via `webhook_id` looked up server-side) before invoking the handler, instead of trusting the header verbatim.
- At minimum, sanitize/validate `shop` with `Utils::ShopValidator` and document clearly that `shop` is not authenticated by the HMAC, so integrators do not treat it as a trusted tenant key without additional verification (e.g., verifying the shop is currently installed and matches other authenticated context).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers an HTTP webhook (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`, and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `B` and `H` from this legitimate delivery (they own this store/webhook, so this is trivially observable).
4. Attacker sends a new POST request directly to the same webhook endpoint, reusing the identical raw body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate(request)` recomputes `HMAC-SHA256(client_secret, B)`, which still equals `H`, so validation passes [7](#0-6) .
6. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the host app processes body `B` as if it came from the victim shop [8](#0-7) .

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
