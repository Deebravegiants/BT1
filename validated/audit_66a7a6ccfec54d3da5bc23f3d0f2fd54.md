This confirms the vulnerability. The `ShopifyAPI::Webhooks::Registry.process` method and `Request` class validate the HMAC only against the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — which are trusted and passed directly to the app's handler as authoritative webhook metadata — are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Title
Webhook `shop-domain` (and other metadata headers) are not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC solely over that body value. However, `Registry.process` trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all read from separate, unsigned HTTP headers — and forwards them as authoritative `WebhookMetadata` to the app's registered handler, which apps use to identify which tenant (shop) the event belongs to.

### Finding Description
The identity binding that should hold is: `hmac_is_valid_for(body) == shop_header_is_authentic_for(body)`. In reality, the gem only proves the former: `Utils::HmacValidator.validate` computes `HMAC-SHA256(client_secret, raw_body)` and compares it to the `hmac` header [1](#0-0) , and `Request#to_signable_string` returns only `@raw_body`, never including `shop`, `topic`, `webhook_id`, or `api_version` [2](#0-1) . Those four values are instead pulled straight from attacker-controllable HTTP headers via `shopify_header` [3](#0-2) [4](#0-3) .

`Registry.process` then only checks `Utils::HmacValidator.validate(request)` before dispatching, and constructs `WebhookMetadata` directly from these unauthenticated header values, which is exactly what is handed to the app's handler as the trusted "which shop is this event for" field: [5](#0-4) . The gem's own documentation instructs developers to treat `data.shop` as the shop domain of the webhook without any further verification [6](#0-5) .

Since the client secret is shared across every shop that installs a given app (it's per-app, not per-shop), any merchant who installs the app on their own store can capture a legitimately-signed webhook delivered to their own endpoint (the HMAC will be valid for that exact body since it was computed by Shopify using the app's `client_secret`), then replay the identical `raw_body` + `hmac` header to the app's shared webhook endpoint while substituting the `x-shopify-shop-domain` header (and optionally `x-shopify-webhook-id`/`x-shopify-topic`) with a victim shop's domain. Because the signature check never covers these header fields, `HmacValidator.validate` still succeeds, and `Registry.process` forwards `shop: <victim-domain>` to the handler as if the event genuinely originated from the victim's store.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for multi-tenant apps: an attacker who controls only their own shop's installation can inject arbitrary webhook payloads that the app processes as belonging to a different shop it also serves. Depending on how the host app's handler uses `data.shop` (e.g., to fetch that shop's stored session/access token and perform actions, update per-shop records, or drive uninstall/redact flows for `shop/redact`), this can lead to cross-tenant data corruption or the app performing privileged actions against a shop the attacker does not own — matching the "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is significant for any app that shares a single webhook endpoint/handler across installations (the common case, as shown in the gem's own docs and Rails example): any low-privileged app-installing user can generate and capture legitimately-signed webhooks against their own shop without needing the app's `client_secret`, then replay them with a forged shop header against the shared endpoint.

### Recommendation
Do not treat header-derived `shop`, `topic`, `webhook_id`, or `api_version` as authenticated by the body HMAC. Either include these fields in the signed payload validation, or require the host application to cross-check the header `shop` value against a known/registered list of shops for the specific `webhook_id`/subscription before trusting it, and document this requirement prominently. At minimum, the `to_signable_string` / HMAC validation contract should be updated to make clear that `shop`, `topic`, and other headers are NOT covered by the signature, so apps don't mistakenly rely on `Registry.process` for tenant isolation.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com`.
2. Attacker triggers an event (e.g., `products/update`) causing Shopify to deliver a webhook to the app's shared endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(client_secret, B)`.
3. Attacker captures `B` and the valid HMAC value from this legitimate delivery.
4. Attacker sends a new POST request directly to the app's webhook endpoint with the same body `B` and the same `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the HMAC [7](#0-6) .
6. `Registry.process` dispatches `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` to the app's handler [8](#0-7) , which now processes attacker-controlled data as if it came from the victim's shop.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
